depends_on('python@2.7.11:', when='+doc', type='build')
# Where 'py' is defined as a provides('py') in the python package, similar to %[+cc+cxx]=gcc.
# NB: '%' is now used to refer to "providing an executable file on the PATH".
# depends_on('%py=python@2.7.11:', when='+doc')
# Since 'python' provides 'py', this should work (proposing "py=python" as a new syntax). This
# says: "depend on python (by default) in +build, and ensure that it provides('py'), or error."
'%py=python@2.7.11:' == '%python@2.7.11:'
# The "type" or "scope" of dependency can be further elaborated within %[+...~...] or
# ^[+...~...], which re-uses the existing variant syntax inside the [].
'%[^build]py=python@2.7.11:' == '%py=python@2.7.11:'
# This moves the "type=('build', 'link', 'run')" into the spec itself!
'^[+build+link]python@2.7.11:' == '^[+build]python@2.7.11: ^[+link]python@2.7.11:'
# TODO: It would probably be good to make more clear what provides('py') is providing, then
# (like using abstractmethods on UnionRule as per https://github.com/pantsbuild/pants/pull/8542)
# require that classes which `provides('py')` actually `provides('[+build+link+run]py')`, or
# *some explicitly denoted subset of those*.
# TODO: This would involve greater requirements to successfully `provides('py')`. If I
# `provides('[+headers]py')`, then Spack will verify that I've defined a method
# e.g. `provides_py_headers()`, which is used as a smoke test after installing the package.
# Note^: we already kind of have this in compiler.py!
# TODO: new version range operations, modelled after python requirements.txt (if only to make it
# easier for python programmers to pick up).
# @2.7.11!: == '>2.7.11' (strict inequality instead of the .99 hack)
'^python@2.7.11!:' == '^python@2.7.11.0.0.1:'  # '@...!:' = '>...' = "greater than ..."
# @:!2.7.11 == '<2.7.11'
'^python@:!2.7.11' == '^python@:2.7.10.99'    # '@:!...' = '<...' = "less than ..."
# @2.7.* == '==2.7.*'
'^python@2.7.*' == '^python@2.7:2.7.99'       # '@X.*' = '>X,<X.99' = "has the root X"
# @2.{6,7}.* == ['==2.6.*', '==2.7.*'] (would need to deprecate using 2.6 to mean 2.6.*)
# [below]: '@X_1.{X_2_A,X_2_B}.X_3' = ['==X_1.X_2_A.X_3', '==X_1.X_2_B.X_3']
# = "covers the alternation of X_2_A and X_2_B within the larger pattern"
'^python@2.{6,7}.*' == '^python@2.6.*,2.7.*'
'^python@2.[6,7].*' == '^python@2.6.*,2.7.*'
# @[!2.7.*] == '!=2.7.*'
'^python@[!2.7.*]' == '^python@:!2.7.*,2.7.*!:'  # '@!...' = '!=...' = "not equal to ..."
# Backwards compatible with existing % sign!
'^[+build+link+run]python@2.7.11:' == '%python@2.7.11:'
# The below equality can be inferred because we are pretending 'python@2.7.11:' only ever
# provides a single "complex dependency" (or "compiler dependency"?) named 'py', for which it
# provides all of +build+link+run. So requesting +build can only resolve to %py+build.
'^[%py+build]python@2.7.11:' == '^[+build]python@2.7.11:'
'^[%py]python@2.7.11:' == '^[%py+build+link+run]python@2.7.11:'
'[%py]python@2.7.11:' == '<%py+build+link+run^python@2.7.11:>%py@3:'
'[%py]python@2.7.11:' == '<%py+build+link+run<^python@2.7.11:>%py@3:>'
'[%py]python@2.7.11:' == '^[%py+build+link+run]python@2.7.11:[%py@3:]'
# In cases where a package may provide "granular artifacts" for more than one virtual provider,
# the provider must be distinguished (in this case, we pretend '%py2' and '%py' are different):
'^[%py2@2.6.*%py@2.6.*]python@2.6.*%py@:!3+build' == '^[%py2+build+link+run%py+build+link+run]python@2.6.*%py@:!3+build'
# Note: the above was *correct*, but the LHS was less specific than it could have been. If the
# version specification is *not* provided, it is "floating", but if it *is* provided and a '@='
# is given as the version string, it is assumed to be the same as the package's
# *concrete* version.
# NB: '@=' is *only* a valid version reference when used in the fore (provides) or aft
# (requires) position for a "complex dependency" / "compiler dependency". There is nothing it
# can unambiguously refer to when used in the middle as the actual abstract or concrete
# spec version.
'^[%py2@=%py@=]python@2.6.*%py@:!3+build~link~run' == '^[%py2@=%py@=]python@2.6.*[%py@:!3+build~link~run]' == '^python@2.6.*%py@:!3+build~link~run'
# NB: The aft (requires) can choose to use [] or not, but the fore (provides) position always
# requires it!
'^[%py@=]python@2.6.*[%py@:!3+build]' == '^[%py@=]python@2.6.*%py@:!3+build'
# TODO^: could also just require all "complex/compiler dependencies" or provides to be enclosed
# in []! Easier to visually differentiate.

# TODO: We have seen '!' used above for negation, but only while referring to a precise single
# lexeme for version strings. Can we apply it more generally?
# Proposal: define an unambiguous grouping methodology for valid spec strings, where each
# character is either:
# (1) An *unpaired*, *prefix* control character ('!' goes *after* this):
#   - '^a' => '^!a'
#   - '%a' => '%!a'
#   - '@a' => '@[!a]' (version lexeme -- 'a' may have multiple sub-components (via comma, '.*',
#                      or '{A,B}'), which '!' distributes over)
#                     (NB: since versions are the only *range* expressions, there is
#                      a significant difference between e.g. '@!:3' = '>3' and '@:!3' = '<3'.
#                      To mitigate this, we *enforce* that '@!...' is illegal,
#                      and '@[!...]' must be used instead.)
#   - '+a' =\> '~a' (special case -- no '!' version of this for boolean variants)
#   - '+a=b' => '+!a=b' (a variant predicate that matches everything *except* '+a=b')
# (2) A prefix or suffix control character which denotes the end of an inclusive range
#     ('!' *SWAPS* the direction!!!!):
#   - 'a:' => ':!a' (version lexeme)
#   - ':a' => 'a!:' (version lexeme)
# (3) A *paired* control character ('!' goes after start):
#   - '[a]' => '[!a]'
# Now, the special-casing with the version ranges above is annoying and error-prone, and I don't
# know what :!a or a!: is supposed to mean without thinking about it. What if we tried to use
# side carats '<' or '>' for non-inclusive version ranges, and *additionally* used them to
# denote the *PARTIAL ORDERING* defined by specs!!
# (1) Introduce 'python@<3' = 'python<3' and 'python@>3' = 'python>3' (strict inequality instead
#     of the .99 hack).
'^python@>2.7.11' == '^python@2.7.11.0.0.1:'  # '@>...' = '>...' = "greater than ..."
# @:!2.7.11 == '<2.7.11'
'^python@<2.7.11' == '^python@:2.7.10.99'    # '@<...' = '<...' = "less than ..."
# (2) Introduce the "stateless" spec expression which all depends_on() and conflicts() can be
#     transformed into. The solver can then work on this conjunction of quantified
#     expressions directly.
depends_on('py-sphinx',      when='+doc', type='build')  # '+doc ^[%py-wheel+build] py-sphinx'
depends_on('openssl', when='+openssl')                 # '+openssl ^ openssl'
depends_on('openssl@:1.0.99', when='@:3.6.9+openssl')  # '@:3.6.9+openssl ^ openssl@<1.1'
# Note that '^[%headers+build %libs+link] <pkg>' is the default configuration for all packages.
depends_on('ncurses',        when='+ncurses')  # '+ncurses ^[{%cxx-headers,%c-headers}+build {%cxx-libs,%c-libs}+link]ncurses'


# (3) Generalize the {A,B} (alternation) operator from above:
# *prefix* top-level control/sentinel characters:
#   1. '+','~' => [VARIANT-NAME]...
#   2. '^' => [PACKAGE-NAME]...
#   3. '%' => [PROVIDER-NAME]...
#   4. '@' => [VERSION-SPEC]
# *prefix* version range markers:
#   5. '<',':','<'
# *suffix* version range markers:
#   6. ':'

# TODO: these are not all the same regex!
# ID = '[a-zA-Z]' '[a-zA-Z_0-9\-]'*

# (defining a throwaway pseudo-function syntax here)

-ALTERNATION-HELPER(joiner, expr) = {
  GROUPING-OPERATOR([expr]) |
  [ALTERNATION-OPERATOR({ -ALTERNATION-HELPER(expr) [joiner] [expr] })]
}

#   The use of `GROUPING-OPERATOR()` here allows for grouping and negation of all sub-version
#   strings of a Version string:
#      - e.g. '^python@2.[!6.7]' == '^python@[!2.6.7]' == '[!^python@2.6.7]'
#      - e.g. '^python@2.{6.6,[!7.18]}' == 'python@2.6.6,[!2.7.18]'
#      - e.g. '[!^python@2.{6.6,[!7.18]}]' == '[!^python@2.6.6] && [python@2.7.18]'
#             => 'python@2.7.18' (this was all done statically, on the *abstract* spec!).

ALTERNATION-OPERATOR(expr) = GROUPING-OPERATOR({
  [expr] |
  '{' [-ALTERNATION-HELPER(',', expr)] '}'
})

#   This produces expressions like "1.{3,4}.{5,6}", which produces a new expression for each
#   combination of alternations (i.e. ["1.3.5", "1.3.6", "1.4.5", "1.4.6"]).

#   It also produces the no-op "python@{2.*,3.*}" which is the same as "python@2.*,3.*". This
#   operator (roughly) multiplies the number of ground variables by the number of expressions in
#   the alternation.

GROUPING-OPERATOR(expr) = {
  [expr] |
  '[' [expr] ']' |
  '[' '!' [expr] ']'
}

#   This produces expressions like "[!^python@<3]", which corresponds to a constraint() call
#   (allowing constraint() calls to also be serialized into the abstract spec).

#   NOTE: this is *COUPLING* two *ORTHOGONAL* concepts, *GROUPING* and *NEGATION*.

#   It's not always clear how to fix a spack spec when it fails to parse. Having a consistent
#   concept of grouping or parentheses (separate from the negation) *could* make spack specs
#   easier to parse for newcomers.

VERSION-SPEC = {
  (':'|'<'|'<=') [VERSION-SPEC-SECTION] => "less than (or equal to)" |
  [VERSION-SPEC-SECTION] ':' => "greater than or equal to" |
  ('>'|'>=') [VERSION-SPEC-SECTION] => "greater than" |
  [VERSION-SPEC] ',' [VERSION-SPEC] |
  [ALTERNATION-OPERATOR(VERSION-SPEC)] => "same as above, but with explicit braces {}" |
  '=' => "placeholder -- the same as the concretized version of the package referred to"
         See above on the new '@=' token.
}

#   This does 3 things:
#   1. adds the new tokens '<=?|>=?' (standard inequality notation) to version specs.
#     -  This should break nothing.
#     - Allows converting e.g. "python@:2.6.99" to the more readable "python@<2.7".
#   2. adds the new '@=' token to refer to whatever the fully concretized version of the inner
#      package is:
#     - e.g. '^[%py@=]python@2.6.6' would be equivalent to
#            '^[%py@2.6.6+build+link+run]python@2.6.6'.
#     - This is more precise (and probably easier to solve for) than e.g. saying
#       '^[%py@2.6.*]python@2.6.6', which is equivalent, but requires the solver to infer
#       the version.
#   3. Adds the new expression 'python@{2.6,2.7}', which is equivalent to 'python@2.6,2.7'.

VERSION-COMPONENT = {
  '[0-9]'+ |
  '\*'
}

#   This adds the '*' component (e.g. '2.6.*'), which corresponds to the python requirements.txt
#   '==2.6.*' expression: see https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers!
#     - e.g. '2.6.*' matches '2.6.5', '2.6beta3', '2.6.7.8', but not '2.7'.

#   Like ALTERNATION-OPERATOR() above, this feature may make the grounding phase slower.

# We assume whatever is parsing this is greedily taking the longest substring:

VERSION-SPEC-SECTION = -ALTERNATION-HELPER('\.', ALTERNATION-OPERATOR([VERSION-COMPONENT]))
VERSION = '@' [VERSION-SPEC]

#   - Each version component can be alternated with {...,...} or negated with [!...]:
#     - e.g. '@2.{3,[!4],[5]}' => [@2.3, @2.5, @2.X \forall X != 4].

# TODO: validate the variant name and value patterns!
VARIANT-NAME = [ID]

%VARIANT-VALUE-BODY = [^[:space:]]

# TODO: all non-boolean variants are "multi valued", so we can split them by comma. Will this
#       continue to be a safe assumption?
VARIANT-VALUE = -ALTERNATION-HELPER(',', ALTERNATION-OPERATOR([%VARIANT-VALUE-BODY]+))
#   - The `+` at the end is a regular expression.
BOOLEAN-VARIANT-SPEC = [VARIANT-NAME]
VALUED-VARIANT = ALTERNATION-OPERATOR([VARIANT-NAME] '=' [VARIANT-VALUE])
-VARIANT-INNER-SPEC = {
  '[\+~]' [BOOLEAN-VARIANT-SPEC] |
  '[[:space:]]+' [VALUED-VARIANT] |
  ALTERNATION-OPERATOR([-VARIANT-INNER-SPEC]) |
  [-VARIANT-INNER-SPEC] [-VARIANT-INNER-SPEC] |
  <empty string: epsilon>
}
VARIANT-SPEC = ALTERNATION-OPERATOR([-VARIANT-INNER-SPEC])

PROVIDER-NAME = [ID]
SINGLE-PROVIDER-SPEC = GROUPING-OPERATOR('%' [PROVIDER-NAME] [VARIANT-SPEC])
PROVIDERS-SPEC =  {
  ALTERNATION-OPERATOR([SINGLE-PROVIDER-SPEC]) |
  [PROVIDERS-SPEC] [PROVIDERS-SPEC] |
  <empty string: epsilon>
}

PACKAGE-NAME = [ID]

THIS-PROVIDES-SPEC = '[' '!'? [PROVIDERS-SPEC] ']'
#   This did not use GROUPING-OPERATOR(), because we *require* that "provides" specifications
#   are wrapped with [], but "requires" are optional (for backwards compatibility).
#     - e.g. '^[%py@=]python@2.6.*[%cc]' == '^[%py@=]python@2.6.*%cc'
THIS-REQUIRES-SPEC = ALTERNATION-OPERATOR([PROVIDERS-SPEC])

# This is called a "node" because it represents all incoming and outgoing relationships.
SPACK-SPEC-NODE = ALTERNATION-OPERATOR({
  [THIS-PROVIDES-SPEC]? [PACKAGE-NAME] [VERSION]? [VARIANT-SPEC] [THIS-REQUIRES-SPEC]?
})

DEPENDENCY = ALTERNATION-OPERATOR({'^' [SPACK-SPEC-NODE]})

SPEC = ALTERNATION-OPERATOR({
  ALTERNATION-OPERATOR([SPACK-SPEC-NODE]) |
  [SPEC] [DEPENDENCY]
})

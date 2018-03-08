/* Scalar values */
sig Superparticle {} {
	Superparticle = Universe.Element
}

/* Domains */
abstract sig Universe { Element: some Superparticle }
one sig UniverseAlpha, UniverseBeta extends Universe {}

/* Common domain */
some sig Particle in Superparticle {} {
	Particle = UniverseAlpha.Element & UniverseBeta.Element
}

/* Database Instance */
one sig Table {
    Follows: Particle -> Particle,
} {
    some Follows
}

/* Lists all follows who follows every idols */
fun query[u: Universe]: set Superparticle {
    { x: u.Element | all y: u.Element |
        (some z: u.Element | z -> y in Table.Follows)
        implies (x -> y in Table.Follows) }
}

/* Safety assertion */
assert queryIsSafe {
    all u, u': Universe | query[u] = query[u']
}

/* Results placeholder */
abstract sig Result {
    Output: set Superparticle
}
one sig ResultAlpha, ResultBeta extends Result {} {
    ResultAlpha.@Output = query[UniverseAlpha]
    ResultBeta.@Output = query[UniverseBeta]
}

/* Invoke the verification on the assertion */
check queryIsSafe for 12

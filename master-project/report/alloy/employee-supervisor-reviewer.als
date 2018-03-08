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
    Employee: Particle -> Particle,
    Supervisor: Particle -> Particle,
    Reviewer: Particle -> Particle -> Particle
}

/* Query functions */
fun query1[u: Universe]: Superparticle -> Superparticle {
    { x, y: u.Element | some b: u.Element |
        (x -> b in Table.Supervisor) and (y -> b in Table.Supervisor) and
        (some l: u.Element | (b -> l in Table.Employee) and
                             ((x -> l in Table.Employee) or (y -> l in Table.Employee))) }
}
fun query2[u: Universe]: Superparticle -> Superparticle {
    { x, y: u.Element | some b, l: u.Element |
        (b -> l in Table.Employee) and
        ((x -> l in Table.Employee) and (x -> b in Table.Supervisor) or
         (y -> l in Table.Employee) and (y -> b in Table.Supervisor)) }
}
fun query3[u: Universe]: set Superparticle {
    { x: u.Element | not some b: u.Element | x -> b in Table.Supervisor }
}
fun query4[u: Universe]: Superparticle -> Superparticle {
    { x, y: u.Element | some t: u.Element |
        (x -> t -> y in Table.Reviewer) or (y -> t -> x in Table.Reviewer) }
}
fun query5[u: Universe]: set Superparticle {
    { b: u.Element |
        (all x: u.Element | some t: u.Element | x -> t -> b in Table.Reviewer) and
        (some y: u.Element | (y -> b in Table.Supervisor) and not (y = b)) }
}

/* Safety assertion */
assert queryIsSafe {
    all u, u': Universe | query5[u] = query5[u']
}

/* Results placeholder */
abstract sig Result {
    OneColOutput: set Superparticle,
    TwoColOutput: Superparticle -> Superparticle
}
one sig ResultAlpha, ResultBeta extends Result {} {
    ResultAlpha.@OneColOutput = query5[UniverseAlpha]
    ResultBeta.@OneColOutput = query5[UniverseBeta]
}

/* Invoke the verification on the assertion */
check queryIsSafe for 10

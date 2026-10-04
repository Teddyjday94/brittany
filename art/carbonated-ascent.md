# Carbonated Ascent

An algorithmic philosophy for pressure released as color.

Carbonated Ascent models a sealed system the moment it opens. Thousands of particles wait at the bottom of a field, each carrying a seeded size, a buoyancy, and a pigment. Released, they rise along a vertical drift that layered noise bends into slow, lazy S-curves. Large particles climb fast and wobble wide. Small ones dawdle and shimmer. You see the algorithm in the gap between those speeds, and every coefficient behind it should read as meticulously crafted, the result of painstaking tuning by someone at the top of computational craft.

Noise acts as the only current. Two octaves of Perlin noise sampled against time push each particle sideways, so neighbors drift in loose schools instead of straight lines. When a particle reaches the surface it pops: a brief ring expands and fades, and a new particle is born at the floor with a fresh seeded size. The system never empties and never repeats. That cycle of birth, ascent, and pop runs as a master-level implementation that holds sixty frames a second without a stutter.

Color comes from a fixed palette of five saturated pigments, drawn with fixed weights so the field keeps its character across seeds. Highlights sit on every particle at the same angle, as if one stage light hung above the whole system. Particles keep full opacity while they rise and only the pop rings fade, so the field reads as solid confetti rather than smoke. The palette calibration is deliberate, the product of deep expertise in how saturated hues sit beside each other.

Interaction stays gentle. A pointer moving through the field acts as a soft repulsor, parting the bubbles the way a straw parts foam, and the field closes back over the gap within a second. Reduced-motion preferences freeze the system into a single, fully composed still frame drawn from the same seed. The algorithm reveals its craft through restraint, with each parameter refined through countless iterations until the motion feels inevitable.

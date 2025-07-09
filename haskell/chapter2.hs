-- Exercise 2.1
f :: Double -> Double
f x = sqrt(1 + x)

-- Exercise 2.2
yRock30 :: Double -> Double
g :: Double
v0 :: Double
v0 = 30
g = -9.8
yRock30 t = v0 * t + g * t**2/2

-- Exercise 2.3
vRock30 :: Double -> Double
vRock30 t = v0 + g*t

-- Exercise 2.4
sinDeg :: Double -> Double
sinDeg x = sin (x * pi / 180)

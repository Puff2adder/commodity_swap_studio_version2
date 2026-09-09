"""Financial calculations, independent of the interface. Rates are continuous decimals."""
import math


def discount(t, r):
    if not math.isfinite(t) or not math.isfinite(r) or t < 0:
        raise ValueError('Use finite rates and nonnegative times.')
    return math.exp(-r*t)


def fair_price(forwards, discounts, quantities=None):
    quantities = [1.0]*len(forwards) if quantities is None else quantities
    if not forwards or len({len(forwards), len(discounts), len(quantities)}) != 1:
        raise ValueError('Inputs must have matching nonempty lengths.')
    if not all(math.isfinite(x) for xs in (forwards, discounts, quantities) for x in xs):
        raise ValueError('Inputs must be finite.')
    if any(d <= 0 for d in discounts) or any(q <= 0 for q in quantities):
        raise ValueError('Discount factors and quantities must be positive.')
    return sum(f*d*q for f,d,q in zip(forwards,discounts,quantities))/sum(d*q for d,q in zip(discounts,quantities))


def value_fixed_payer(forwards, discounts, quantities, fixed):
    fair_price(forwards, discounts, quantities)  # Validate matching inputs.
    return sum(d*q*(f-fixed) for f,d,q in zip(forwards,discounts,quantities))


def buyer_cost(physical_price, index_price, fixed, actual, hedged):
    if actual <= 0 or hedged < 0:
        raise ValueError('Actual quantity must be positive; hedge quantity nonnegative.')
    return actual*physical_price-hedged*(index_price-fixed)


def carry(spot, rate, storage, convenience, time):
    if spot <= 0 or time <= 0:
        raise ValueError('Spot and time must be positive.')
    return spot*math.exp((rate+storage-convenience)*time)


def implied_yield(spot, forward, rate, storage, time):
    if spot <= 0 or forward <= 0 or time <= 0:
        raise ValueError('Spot, forward and time must be positive.')
    return rate+storage-math.log(forward/spot)/time

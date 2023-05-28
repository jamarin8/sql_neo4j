
from itertools import permutations

def fix_year(year: object, min_year: object = 1900, max_year: object = 2023) -> object:
    """Attempt to fix an out-of-range year by permuting its digits."""
    perms = [''.join(p) for p in permutations(year)]
    for yr in perms:
        if min_year <= int(yr) <= max_year:
            return yr
    return None  # no valid permutations found

def clean_dates(df, column, min_year=1900, max_year=2023):
    for i in df.index:
        year = df.loc[i, column][:4]
        if not (min_year <= int(year) <= max_year):
            # Try to fix the year
            new_year = fix_year(year)
            if new_year is not None:
                # If a valid permutation was found, replace the year
                df.loc[i, column] = new_year + df.loc[i, column][4:]
            else:
                # If no valid permutations, replace with a default date
                df.loc[i, column] = '1900-01-01 00:00:00'
    return df
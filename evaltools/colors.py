
import seaborn as sns
import math
from typing import List, Tuple

"""
Color schemes.
"""

districtr = [
    "#0099cd", "#ffca5d", "#00cd99", "#99cd00", "#cd0099", "#9900cd", "#8dd3c7",
    "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#bc80bd",
    "#ccebc5", "#ffed6f", "#ffffb3", "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c",
    "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a", "#b15928",
    "#64ffda", "#00B8D4", "#A1887F", "#76FF03", "#DCE775", "#B388FF", "#FF80AB",
    "#D81B60", "#26A69A", "#FFEA00", "#6200EA"
]

def redblue(n) -> List[Tuple]:
    """
    Generates a red/white/blue color palette in `n` colors with white at the
    `mid`th index.

    Args:
        n (int): The number of colors to generate.

    Returns:
        List of RGB tuples.
    """
    midpoint = math.ceil(n/2)
    
    # To get the appropriately-toned blues and reds, we create a list of colors,
    # then select the first section of each color.
    blues = list(
        sns.color_palette("coolwarm", as_cmap=False, n_colors=n+2)
    )[:midpoint]
    reds = list(
        sns.color_palette("coolwarm", as_cmap=False, n_colors=n+2)
    )[-midpoint:]
    
    return list(reversed(reds)) + list(reversed(blues))


def flare(n):
    return list(sns.color_palette("flare", as_cmap=False, n_colors=n))

def purples(n):
    return list(sns.color_palette("Purples", as_cmap=False, n_colors=n))
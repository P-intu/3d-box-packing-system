from decimal import Decimal
from itertools import permutations
from box_selection.models import Box, Order


def get_item_orientations(length, width, height):
    """
    Returns all unique 3D rotations for an item.
    """
    return list(set(permutations([length, width, height])))


def items_overlap(pos1, dim1, pos2, dim2):
    """
    Returns True if two 3D boxes overlap.
    Touching at the boundary is allowed (not an overlap).
    """
    x1, y1, z1 = pos1
    l1, w1, h1 = dim1
    x2, y2, z2 = pos2
    l2, w2, h2 = dim2

    # Check if separated along any axis
    if x1 + l1 <= x2 or x2 + l2 <= x1:
        return False
    if y1 + w1 <= y2 or y2 + w2 <= y1:
        return False
    if z1 + h1 <= z2 or z2 + h2 <= z1:
        return False

    return True


def can_place_item(pos, dim, box_dims, placed_items):
    """
    Checks if an item fits inside the box and doesn't overlap with placed items.
    """
    x, y, z = pos
    l, w, h = dim
    box_l, box_w, box_h = box_dims

    # Must stay inside box limits
    if x + l > box_l or y + w > box_w or z + h > box_h:
        return False

    # Must not overlap with any existing item
    for placed_pos, placed_dim in placed_items:
        if items_overlap(pos, dim, placed_pos, placed_dim):
            return False

    return True


def can_pack_items(items, box_dims):
    """
    Attempts to pack all items into a box using 3D anchor points.
    """
    placed_items = []  # List of tuples: (position, dimension)
    anchors = [(0.0, 0.0, 0.0)]

    for item in items:
        placed = False
        orientations = get_item_orientations(item[0], item[1], item[2])

        # Prioritize lower positions first (z, then y, then x)
        anchors.sort(key=lambda p: (p[2], p[1], p[0]))

        for anchor in list(anchors):
            for ori in orientations:
                if can_place_item(anchor, ori, box_dims, placed_items):
                    placed_items.append((anchor, ori))
                    anchors.remove(anchor)

                    # Add new anchor points from the placed item
                    x, y, z = anchor
                    l, w, h = ori
                    new_pts = [(x + l, y, z), (x, y + w, z), (x, y, z + h)]
                    for pt in new_pts:
                        if pt not in anchors:
                            anchors.append(pt)

                    placed = True
                    break
            if placed:
                break

        if not placed:
            return False

    return True


def select_best_box(order, candidate_boxes=None):
    """
    Finds the smallest, cheapest box that can fit all items in the order.
    """
    order_items = order.items.select_related('product').all()
    if not order_items.exists():
        return None

    # 1. Expand quantities into individual item dimensions and sum weights
    expanded_items = []
    total_weight = Decimal('0.00')

    for item in order_items:
        p = item.product
        for _ in range(item.quantity):
            expanded_items.append((float(p.length), float(p.width), float(p.height)))
            total_weight += p.weight

    # 2. Sort items by volume descending (largest first)
    expanded_items.sort(key=lambda d: d[0] * d[1] * d[2], reverse=True)

    # 3. Get candidate boxes and filter by weight capacity
    if candidate_boxes is None:
        boxes = list(Box.objects.all())
    else:
        boxes = list(candidate_boxes)

    valid_boxes = [b for b in boxes if b.max_weight >= total_weight]

    # 4. Sort candidate boxes by volume (ascending), then cost (ascending)
    valid_boxes.sort(
        key=lambda b: (
            float(b.internal_length * b.internal_width * b.internal_height),
            float(b.cost)
        )
    )

    # 5. Test packing in candidate boxes
    for box in valid_boxes:
        box_dims = (float(box.internal_length), float(box.internal_width), float(box.internal_height))
        if can_pack_items(expanded_items, box_dims):
            return box

    return None

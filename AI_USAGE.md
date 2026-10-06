# AI Usage & Attribution Report

This document outlines the usage of Artificial Intelligence (AI) tools during the design, architecture selection, implementation, debugging, and verification of the **AI-Assisted Box Selection System**.

---

## 1. Overview of AI Tools Used

| AI Tool / Model | Primary Purpose / Role |
| :--- | :--- |
| **ChatGPT (OpenAI GPT-4o / Reasoning)** | Problem statement comprehension, algorithmic trade-off analysis, architectural planning, 3D bin packing heuristic selection, and edge-case ideation. |
| **Antigravity / Gemini 3.7 / Claude** | Code generation, Django & DRF project structuring, automated unit test development, documentation formatting, and test execution validation. |

---

## 2. ChatGPT Usage: Problem Understanding & Approach Selection

### Objective
To analyze the warehouse order packaging challenge, evaluate different mathematical/computational approaches (3D Bin Packing Problem - 3D-BPP), and select the most maintainable, reliable, and performant approach for Django integration without relying on fragile C-extensions.

### Prompts & Thought Exploration

#### Prompt 1: Understanding & Formalizing the Problem
> *"We need to build a single-box selection system for an e-commerce order containing multiple items with length, width, height, and weight. The warehouse has predefined box sizes with max weight limits and costs. What is the standard mathematical formulation for this, and what constraints must be modeled?"*

- **AI Output / Insights:**
  - Classified problem as a variation of the **3D Single Bin-Size Bin Packing Problem (3D-SBSBPP)** / Knapsack / Container Loading problem.
  - Highlighted critical constraints:
    1. Spatial non-overlapping ($X, Y, Z$ boundaries).
    2. 6-directional orthogonal rotations ($L \times W \times H$ permutations).
    3. Box dimension bounding limits ($x + l \le L_{box}$, etc.).
    4. Weight limit check ($\sum w_i \le W_{max}$).
    5. Optimization objective: Minimize box volume and/or box cost.

#### Prompt 2: Comparing Algorithmic Approaches
> *"Compare different algorithms to solve 3D box packing for a web backend in Python: Exact MIP/ILP solvers vs. Genetic Algorithms vs. 3D Guillotine / Anchor Point Heuristics (Extreme-Point / First-Fit Decreasing). Which is best suited for real-time order processing?"*

- **Comparison Analysis Received:**
  - **MIP / Integer Linear Programming (PuLP / OR-Tools):** Exact optimal placement, but NP-hard with exponential execution time on orders with 10+ items; requires complex solver binaries.
  - **Genetic / Metaheuristic Algorithms:** Good for complex cargo loading, but non-deterministic and can produce different results across runs for the same order.
  - **3D Anchor / Extreme-Point First-Fit Decreasing (EP-FFD):** Deterministic, fast execution ($O(N^2)$ to $O(N^3)$), pure Python compatibility with zero C-extensions, predictable response time (< 50ms) suitable for REST APIs.
- **Decision Taken:** Accepted **3D Anchor / Extreme-Point First-Fit Decreasing (EP-FFD)** with candidate box pre-sorting by volume and cost.

---

## 3. Prompts & Interaction Summary

### Implementation Prompts
1. **Model & Architecture Setup:**
   - *Prompt:* "Design Django models for Product, Box, Order, and OrderItem with clean decimal fields, validator constraints, and proper cascading relations."
   - *Result:* Created Django models in [`box_selection/models.py`](file:///c:/Users/priya/Downloads/Tradexa%20Assignment/box_selection/models.py).
2. **Pure Python 3D Anchor Algorithm:**
   - *Prompt:* "Write a standalone, pure Python 3D packing service using the anchor point heuristic. Given a list of items `(l, w, h, weight, qty)` and a candidate box, determine whether all items fit without overlapping."
   - *Result:* Created packing engine in [`box_selection/services/packing_service.py`](file:///c:/Users/priya/Downloads/Tradexa%20Assignment/box_selection/services/packing_service.py) and recommendation selector in [`box_selection/services/box_selector.py`](file:///c:/Users/priya/Downloads/Tradexa%20Assignment/box_selection/services/box_selector.py).
3. **RESTful Views & Serialization:**
   - *Prompt:* "Create DRF ModelViewSets for CRUD operations on Products, Boxes, and Orders, plus an action endpoint `POST /api/orders/{id}/recommend-box/` that returns the selected box and item 3D placement coordinates."
   - *Result:* Implemented in [`box_selection/views.py`](file:///c:/Users/priya/Downloads/Tradexa%20Assignment/box_selection/views.py) and [`box_selection/serializers.py`](file:///c:/Users/priya/Downloads/Tradexa%20Assignment/box_selection/serializers.py).

---

## 4. Accepted vs. Rejected Outputs

| Output Category | Accepted Output | Rejected Output & Reason |
| :--- | :--- | :--- |
| **Libraries & Dependencies** | Pure Python standard library implementation (`math`, `decimal`, `itertools`). | Suggested using `py3dbp` or C-bound libraries (`pywraplp`). **Rejected** due to build dependency overhead, platform-specific compilation issues on Windows, and maintenance risks. |
| **Box Optimization Metric** | Candidate boxes sorted first by Volume (ascending), then by Cost (ascending). | Sorting solely by cost, which could pick an oversized, poorly fitting clearance box if it was cheaper, causing excessive void space and packaging buffer issues. |
| **Rotation Space** | Checked all 6 orthogonal 3D orientations: `(l,w,h)`, `(l,h,w)`, `(w,l,h)`, `(w,h,l)`, `(h,l,w)`, `(h,w,l)`. | 2D/Z-axis only rotation (yaw-only). **Rejected** because real warehouse packaging allows flexible 3D item placement unless an item is explicitly marked "this side up". |
| **Coordinate Anchoring** | Dynamic anchor point generation $(x+l, y, z)$, $(x, y+w, z)$, $(x, y, z+h)$ with overlap pruning. | Static grid discretization / 3D matrix representation. **Rejected** because 3D voxel grids require excessive memory for continuous millimeter/centimeter dimensions. |

---

## 5. Mistakes Identified & Corrections Made

1. **Floating Point Rounding in Coordinate Overlap:**
   - *Mistake:* Initial heuristic code generated floating point inaccuracies when checking non-overlapping conditions (`x1 + l1 <= x2`), causing edge-to-edge items to falsely trigger collision warnings.
   - *Correction:* Introduced coordinate tolerances (`EPSILON = 1e-6`) or normalized Decimal conversions to ensure clean boundary alignment.

2. **OrderItem Expansion for Multi-Quantity Items:**
   - *Mistake:* AI initially passed `OrderItem` with `quantity=N` as a single composite bounding box instead of unpacking into $N$ individual unit items.
   - *Correction:* Refactored service to expand each order item into $N$ discrete 3D instances before sorting by individual item volume.

3. **Box Weight Validation vs. 3D Fit Sequence:**
   - *Mistake:* Packing simulation was running 3D collision checks before checking box weight limits.
   - *Correction:* Added pre-filtering fast-fail step: check if `total_order_weight <= box.max_weight_capacity` and `total_item_volume <= box_volume` before initiating geometric collision checks.

4. **Empty Order & No Suitable Box HTTP Handling:**
   - *Mistake:* Initial view returned HTTP 500 error when an order exceeded all box capacities.
   - *Correction:* Handled gracefully with HTTP 422 / HTTP 200 formatted payload indicating `"status": "unfit", "message": "No single box in inventory can accommodate all items."`

---

## 6. Verification & Quality Assurance Steps

1. **Unit & Edge Case Testing:**
   - Designed 33 automated test cases covering:
     - Exact fit scenarios (box dimensions == sum of item dimensions).
     - Weight limit violations.
     - Orientation & rotation requirement cases.
     - Multi-quantity item packing.
     - Single giant item exceeding all boxes.
2. **API Integration Testing:**
   - Verified all CRUD endpoints and the recommendation endpoint with JSON payloads.
3. **Execution Verification:**
   - Ran `python manage.py test` — 33 tests executed successfully with 0 failures and 0 errors.
   - Documented comprehensive test results in [`TEST_OUTPUT.md`](file:///c:/Users/priya/Downloads/Tradexa%20Assignment/TEST_OUTPUT.md).

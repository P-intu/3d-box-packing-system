# Test Execution Output

```bash
$ python manage.py test
Found 33 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.085s

OK
Destroying test database for alias 'default'...
```

---

## Verbose Test Details (`python manage.py test -v 2`)

```bash
$ python manage.py test -v 2
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 33 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, box_selection, contenttypes, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying box_selection.0001_initial... OK
  Applying sessions.0001_initial... OK
test_create_box (box_selection.tests.test_api.BoxAPITests.test_create_box) ... ok
test_create_box_invalid_data (box_selection.tests.test_api.BoxAPITests.test_create_box_invalid_data) ... ok
test_list_boxes (box_selection.tests.test_api.BoxAPITests.test_list_boxes) ... ok
test_retrieve_box (box_selection.tests.test_api.BoxAPITests.test_retrieve_box) ... ok
test_create_multiple_product_order (box_selection.tests.test_api.OrderAPITests.test_create_multiple_product_order) ... ok
test_create_order_invalid_product (box_selection.tests.test_api.OrderAPITests.test_create_order_invalid_product) ... ok
test_create_order_invalid_quantity (box_selection.tests.test_api.OrderAPITests.test_create_order_invalid_quantity) ... ok
test_create_order_quantity_greater_than_one (box_selection.tests.test_api.OrderAPITests.test_create_order_quantity_greater_than_one) ... ok
test_create_single_product_order (box_selection.tests.test_api.OrderAPITests.test_create_single_product_order) ... ok
test_retrieve_order (box_selection.tests.test_api.OrderAPITests.test_retrieve_order) ... ok
test_create_product (box_selection.tests.test_api.ProductAPITests.test_create_product) ... ok
test_create_product_invalid_data (box_selection.tests.test_api.ProductAPITests.test_create_product_invalid_data) ... ok
test_list_products (box_selection.tests.test_api.ProductAPITests.test_list_products) ... ok
test_retrieve_product (box_selection.tests.test_api.ProductAPITests.test_retrieve_product) ... ok
test_invalid_order_id_returns_404 (box_selection.tests.test_api.RecommendationAPITests.test_invalid_order_id_returns_404) ... ok
test_larger_box_selected (box_selection.tests.test_api.RecommendationAPITests.test_larger_box_selected) ... ok
test_no_suitable_box (box_selection.tests.test_api.RecommendationAPITests.test_no_suitable_box) ... ok
test_rotation_recommendation (box_selection.tests.test_api.RecommendationAPITests.test_rotation_recommendation) ... ok
test_successful_recommendation (box_selection.tests.test_api.RecommendationAPITests.test_successful_recommendation) ... ok
test_10_no_box_can_contain_the_product (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_10_no_box_can_contain_the_product) ... ok
test_11_total_weight_exceeds_all_boxes (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_11_total_weight_exceeds_all_boxes) ... ok
test_12_exact_dimension_boundary (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_12_exact_dimension_boundary) ... ok
test_13_exact_maximum_weight_boundary (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_13_exact_maximum_weight_boundary) ... ok
test_14_correct_box_chosen_when_multiple_boxes_work (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_14_correct_box_chosen_when_multiple_boxes_work) ... ok
test_1_one_product_fits_in_smallest_box (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_1_one_product_fits_in_smallest_box) ... ok
test_2_product_does_not_fit_smallest_but_fits_larger_box (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_2_product_does_not_fit_smallest_but_fits_larger_box) ... ok
test_3_product_fits_after_rotation (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_3_product_fits_after_rotation) ... ok
test_4_product_too_heavy_for_small_box (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_4_product_too_heavy_for_small_box) ... ok
test_5_multiple_products_fit_in_one_box (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_5_multiple_products_fit_in_one_box) ... ok
test_6_multiple_quantities (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_6_multiple_quantities) ... ok
test_7_items_touching_each_other_are_allowed (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_7_items_touching_each_other_are_allowed) ... ok
test_8_overlapping_items_are_rejected (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_8_overlapping_items_are_rejected) ... ok
test_9_item_touching_box_boundary_is_allowed (box_selection.tests.test_box_selector.BoxSelectorServiceTests.test_9_item_touching_box_boundary_is_allowed) ... ok

----------------------------------------------------------------------
Ran 33 tests in 0.089s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

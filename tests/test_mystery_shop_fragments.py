from __future__ import annotations

import re
import unittest
from types import SimpleNamespace

from custom.action.mystery_shop_fragments import (
    CONFIG_NODE,
    FRAGMENT_NODE,
    ApplyMysteryShopFragmentConfig,
    fragment_pattern,
    selected_fragment_names,
)


class _Context:
    def __init__(self, attach: dict | None):
        self.node = {"attach": attach} if attach is not None else None
        self.overrides: list[dict] = []
        self.override_ok = True

    def get_node_data(self, name: str):
        self.assert_name = name
        return self.node

    def override_pipeline(self, value: dict):
        self.overrides.append(value)
        return self.override_ok


def _argv():
    return SimpleNamespace(custom_action_param="")


class MysteryShopFragmentConfigTest(unittest.TestCase):
    def test_fragment_pattern_matches_shop_card_without_spaces(self):
        card = "剑心 · 卫鲤碎片".replace(" ", "").replace("　", "")
        self.assertRegex(card, fragment_pattern("剑心·卫鲤"))

    def test_selected_names_come_only_from_attach(self):
        attach = {"剑心·卫鲤": True, "双焰·小椒": False, "极刃·血影": True}
        self.assertEqual(
            selected_fragment_names(attach),
            ["剑心·卫鲤", "极刃·血影"],
        )

    def test_no_selection_leaves_fragment_nodes_disabled(self):
        context = _Context({})
        result = ApplyMysteryShopFragmentConfig().run(context, _argv())
        self.assertTrue(result.success)
        self.assertEqual(context.assert_name, CONFIG_NODE)
        self.assertEqual(context.overrides, [])

    def test_selected_full_names_are_written_to_eighth_slot_only(self):
        context = _Context({"剑心·卫鲤": True, "双焰·小椒": False, "极刃·血影": True})
        result = ApplyMysteryShopFragmentConfig().run(context, _argv())
        self.assertTrue(result.success)
        self.assertEqual(len(context.overrides), 1)
        override = context.overrides[0]
        expected = [
            fragment_pattern("剑心·卫鲤"),
            fragment_pattern("极刃·血影"),
        ]
        self.assertEqual(set(override), {FRAGMENT_NODE})
        node = override[FRAGMENT_NODE]
        self.assertTrue(node["enabled"])
        self.assertEqual(node["recognition"]["param"]["expected"], expected)
        for pattern in node["recognition"]["param"]["expected"]:
            self.assertIsNotNone(
                re.fullmatch(pattern, "剑心·卫鲤碎片")
                or re.fullmatch(pattern, "极刃·血影碎片")
            )

    def test_any_truthy_attach_key_is_purchased(self):
        context = _Context({"白·小黑": True})
        result = ApplyMysteryShopFragmentConfig().run(context, _argv())
        self.assertTrue(result.success)
        self.assertEqual(len(context.overrides), 1)
        expected = context.overrides[0][FRAGMENT_NODE]["recognition"]["param"]["expected"]
        self.assertEqual(expected, [fragment_pattern("白·小黑")])


if __name__ == "__main__":
    unittest.main()

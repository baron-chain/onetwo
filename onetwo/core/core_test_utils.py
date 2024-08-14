# Copyright 2024 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for OneTwo unit tests."""

import collections
from collections.abc import Mapping
import json
import pprint
from typing import Any
import unittest
from onetwo.core import results


class CounterAssertions(unittest.TestCase):
  """Mixin class for counter assertions."""

  # pylint: disable=invalid-name
  def assertCounterEqual(
      self,
      counter_first: collections.Counter[str],
      counter_second: collections.Counter[str],
  ) -> None:
    # Remove zero values.
    first = counter_first - collections.Counter()
    second = counter_second - collections.Counter()
    message = f'A - B contains: {pprint.pformat(first - second)}\n'
    message += f'B - A contains: {pprint.pformat(second - first)}'
    return self.assertEqual(dict(first), dict(second), message)


def maybe_read_file(filepath: str) -> str:
  """Returns the contents of the file if it exists, or else empty string."""
  try:
    with open(filepath) as f:
      file_contents = f.read()
    return file_contents
  except IOError:
    return ''


def maybe_read_json(filepath: str) -> Mapping[str, Any] | None:
  """Returns the file contents as JSON, or None if there is a problem."""
  file_contents = maybe_read_file(filepath)
  try:
    return json.loads(file_contents)
  except json.JSONDecodeError:
    return None


class MockTimer:
  """Mock timer for use in unit tests."""

  def __init__(self):
    self._current_time = 0

  def __call__(self) -> float:
    self._current_time += 1
    return float(self._current_time)


def reset_fields(
    er: list[results.ExecutionResult] | results.ExecutionResult,
    reset_values: Mapping[str, Any],
):
  """Recursively resset the given fields in the given execution result(s).

  Args:
    er: The ExecutionResult or list thereof to reset fields in.
    reset_values: Mapping field_name to the value to set when resetting.

  Returns:
    None.
  """
  if isinstance(er, list):
    for sub_er in er:
      reset_fields(sub_er, reset_values)
    return

  for name, value in reset_values.items():
    setattr(er, name, value)

  for stage in er.stages:
    reset_fields(stage, reset_values)


def reset_times(
    er: list[results.ExecutionResult] | results.ExecutionResult,
) -> None:
  """Resets the start and end times in the given execution result(s)."""
  reset_fields(er, {'start_time': 0.0, 'end_time': 0.0})

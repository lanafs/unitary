# Copyright 2022 Google
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from typing import Iterator, Optional, Sequence, Union
import abc
import enum

import cirq


def _to_int(value: Union[enum.Enum, int]) -> int:
    return value.value if isinstance(value, enum.Enum) else value


class QuantumEffect(abc.ABC):
    @abc.abstractmethod
    def effect(self, *objects) -> Iterator[cirq.Operation]:
        """Apply the Quantum Effect to the QuantumObjects."""

    def num_dimension(self) -> Optional[int]:
        """Required Qid dimension.  If any allowed, return None."""
        return None

    def num_objects(self) -> Optional[int]:
        """Number of quantum objects allowed.

        If any allowed, return None.
        """
        return None

    def _verify_objects(self, *objects):
        if self.num_objects() is not None and len(objects) != self.num_objects():
            raise ValueError(f"Cannot apply effect to {len(objects)} qubits.")

        required_dimension = self.num_dimension()
        for q in objects:
            if (required_dimension is not None) and (
                q.num_states != required_dimension
            ):
                raise ValueError(
                    f"Cannot apply effect to qids of dimension {required_dimension}."
                )
            if q.board is None:
                raise ValueError("Piece must be on a board to apply effects.")

    def __call__(self, *objects):
        """Apply the Quantum Effect to the objects."""
        self._verify_objects(*objects)
        board = objects[0].board
        for op in self.effect(*objects):
            board.add(op)


class QuantumIf:
    def effect(self, *objects) -> Iterator[cirq.Operation]:
        pass

    def __call__(self, *objects):
        return QuantumThen(*objects)


class QuantumThen(QuantumEffect):
    def __init__(self, *objects):
        self.control_objects = list(objects)
        self.condition = [1] * len(self.control_objects)
        self.then_effect = None

    def equals(
        self, *conditions: Union[enum.Enum, int, Sequence[Union[enum.Enum, int]]]
    ) -> "QuantumThen":
        if len(conditions) != len(self.control_objects):
            raise ValueError(
                f"Not able to equate {len(self.control_objects)} qubits with {len(conditions)} conditions"
            )
        if isinstance(conditions, (enum.Enum, int)):
            conditions = [conditions]
        self.condition = [_to_int(cond) for cond in conditions]
        return self

    def then(self, effect):
        self.then_effect = effect
        return self

    def effect(self, *objects):
        for idx, cond in enumerate(self.condition):
            if cond == 0 and self.control_objects[idx].num_states == 2:
                yield cirq.X(self.control_objects[idx].qubit)

        for op in self.then_effect.effect(*objects):
            yield op.controlled_by(*[q.qubit for q in self.control_objects])


quantum_if = QuantumIf()

#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import unittest

import torch
from aepsych.acquisition.monotonic_rejection import MonotonicMCLSE
from aepsych.generators import OptimizeAcqfGenerator, SobolGenerator
from aepsych.models.gp_classification import GPClassificationModel
from aepsych.strategy import Strategy
from aepsych.models.utils import select_inducing_points
from aepsych.models.inducing_point_allocators import SobolAllocator


class TestStrategyGPU(unittest.TestCase):
    def test_gpu_no_model_generator_warn(self):
        with self.assertWarns(UserWarning):
            Strategy(
                lb=[0.0],
                ub=[1.0],
                stimuli_per_trial=1,
                outcome_types=["binary"],
                min_asks=1,
                generator=SobolGenerator(lb=[0], ub=[1]),
                use_gpu_generating=True,
            )

    def test_no_gpu_acqf(self):
        with self.assertWarns(UserWarning):
            Strategy(
                lb=[0.0],
                ub=[1.0],
                stimuli_per_trial=1,
                outcome_types=["binary"],
                min_asks=1,
                model=GPClassificationModel(inducing_points=select_inducing_points(inducing_size=10, allocator=SobolAllocator(bounds=torch.stack([torch.tensor([0.0]), torch.tensor([1.0])]))), dim=1),
                generator=OptimizeAcqfGenerator(acqf=MonotonicMCLSE, lb=[0.0], ub=[1.0]),
                use_gpu_generating=True,
            )


if __name__ == "__main__":
    unittest.main()

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
from aepsych.models.inducing_point_allocators import SobolAllocator


class TestStrategyGPU(unittest.TestCase):
    def test_gpu_no_model_generator_warn(self):
        with self.assertWarns(UserWarning):
            Strategy(
                lb=[0],
                ub=[1],
                stimuli_per_trial=1,
                outcome_types=["binary"],
                min_asks=1,
                generator=SobolGenerator(lb=[0], ub=[1]),
                use_gpu_generating=True,
            )

    def test_no_gpu_acqf(self):
        with self.assertWarns(UserWarning):
            Strategy(
                lb=[0],
                ub=[1],
                stimuli_per_trial=1,
                outcome_types=["binary"],
                min_asks=1,
                model=GPClassificationModel(lb=[0], ub=[1], inducing_point_method=SobolAllocator(bounds=torch.stack([torch.tensor([0]), torch.tensor([1])]))),
                generator=OptimizeAcqfGenerator(acqf=MonotonicMCLSE),
                use_gpu_generating=True,
            )


if __name__ == "__main__":
    unittest.main()

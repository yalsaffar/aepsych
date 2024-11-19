#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import time
import unittest

import numpy as np
import torch
from aepsych.acquisition import MCLevelSetEstimation
from aepsych.config import Config
from aepsych.generators import OptimizeAcqfGenerator
from aepsych.models import GPClassificationModel, PairwiseProbitModel
from botorch.acquisition.preference import AnalyticExpectedUtilityOfBestOption
from sklearn.datasets import make_classification
from aepsych.models.inducing_point_allocators import SobolAllocator
from aepsych.models.utils import select_inducing_points

class TestOptimizeAcqfGenerator(unittest.TestCase):
    def test_time_limits(self):
        seed = 1
        torch.manual_seed(seed)
        np.random.seed(seed)

        X, y = make_classification(
            n_samples=100,
            n_features=8,
            n_redundant=3,
            n_informative=5,
            random_state=1,
            n_clusters_per_class=4,
        )
        X, y = torch.Tensor(X), torch.Tensor(y)
        lb = -3 * torch.ones(8)
        ub = 3 * torch.ones(8)
        inducing_size = 10
        bounds = torch.stack([lb, ub])
        inducing_points = select_inducing_points(inducing_size=inducing_size, allocator=SobolAllocator(bounds=bounds))

        model = GPClassificationModel(
            inducing_points=inducing_points,
            max_fit_time=0.5,
            inducing_size=inducing_size,
        )

        model.fit(X, y)
        generator = OptimizeAcqfGenerator(
            acqf=MCLevelSetEstimation, acqf_kwargs={"beta": 1.96, "target": 0.5}, lb=lb, ub=ub,
        )

        start = time.time()
        generator.gen(1, model)
        end = time.time()
        long = end - start
        generator = OptimizeAcqfGenerator(
            acqf=MCLevelSetEstimation,
            acqf_kwargs={"beta": 1.96, "target": 0.5},
            max_gen_time=0.1,
            lb=lb,
            ub=ub,
        )

        start = time.time()
        generator.gen(1, model)
        end = time.time()
        short = end - start

        # very loose test because fit time is only approximately computed
        # on very fast machines, short sometimes actually wins, but hopefully not by
        # much
        self.assertTrue(long - short > -0.05, f"Long time: {long}, short time: {short}")

    def test_instantiate_eubo(self):
        config = """
        [common]
        lb = [-1]
        ub = [1]

        [OptimizeAcqfGenerator]
        acqf = AnalyticExpectedUtilityOfBestOption
        stimuli_per_trial = 2
        """
        generator = OptimizeAcqfGenerator.from_config(Config(config_str=config))
        self.assertTrue(generator.acqf == AnalyticExpectedUtilityOfBestOption)

        # need a fitted model in order to instantiate the acqf successfully
        model = PairwiseProbitModel(lb=[-1], ub=[1])
        train_x = torch.Tensor([-0.5, 1, 0.5, -1]).reshape((2, 1, 2))
        train_y = torch.Tensor([0, 1])
        model.fit(train_x, train_y)
        acqf = generator._instantiate_acquisition_fn(model=model)
        self.assertTrue(isinstance(acqf, AnalyticExpectedUtilityOfBestOption))


if __name__ == "__main__":
    unittest.main()

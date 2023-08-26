"""Abstract base class for deep learning networks."""

__author__ = ["Withington", "TonyBagnall"]

from abc import ABC, abstractmethod

import numpy as np

from sktime.base import BaseObject
from sktime.forecasting.base import BaseForecaster


class BaseDeepNetwork(BaseObject, ABC):
    """Abstract base class for deep learning networks."""

    @abstractmethod
    def build_network(self, input_shape, **kwargs):
        """Construct a network and return its input and output layers.

        Parameters
        ----------
        input_shape : tuple
            The shape of the data fed into the input layer

        Returns
        -------
        input_layer : a keras layer
        output_layer : a keras layer
        """
        ...


class BaseDeepNetworkPyTorch(BaseForecaster, ABC):
    """Abstract base class for deep learning networks using torch.nn."""

    _tags = {
        "python_dependencies": "torch",
    }

    def __init__(self):
        super().__init__()

    def _fit(self, y, X, fh):
        """Fit the network.

        Changes to state:
            writes to self._network.state_dict

        Parameters
        ----------
        X : iterable-style or map-style dataset
            see (https://pytorch.org/docs/stable/data.html) for more information
        """
        dataloader = self.build_pytorch_train_dataloader(y)
        self.network.train()

        for _ in range(self.num_epochs):
            for x, y in dataloader:
                y_pred = self.network(x)
                loss = self._criterion(y_pred, y)
                self._optimizer.zero_grad()
                loss.backward()
                self._optimizer.step()

        # self._fh = self.pred_len

    def _predict(self, X, **kwargs):
        """Predict with fitted model."""
        from torch import cat

        dataloader = self.build_pytorch_pred_dataloader(X)

        y_pred = []
        for x, _ in dataloader:
            y_pred.append(self.network(x).detach())
        y_pred = cat(y_pred, dim=0).view(-1, y_pred[0].shape[-1]).numpy()
        return y_pred

    def build_pytorch_train_dataloader(self, y):
        """Build PyTorch DataLoader for training."""
        from torch.utils.data import DataLoader

        if self.custom_dataset_train:
            if hasattr(self.custom_dataset_train, "build_dataset") and callable(
                self.custom_dataset_train.build_dataset
            ):
                self.custom_dataset_train.build_dataset(y)
                dataset = self.custom_dataset_train
            else:
                raise NotImplementedError(
                    "Custom Dataset `build_dataset` method is not available. Please "
                    f"refer to the {self.__class__.__name__}.build_dataset "
                    "documentation."
                )
        else:
            dataset = PyTorchDataset(
                y=y,
                seq_len=self.network.seq_len,
                pred_len=self.network.pred_len,
                scale=self.scale,
            )

        return DataLoader(
            dataset,
            self.batch_size,
            shuffle=self.shuffle,
        )

    def build_pytorch_pred_dataloader(self, y):
        """Build PyTorch DataLoader for prediction."""
        from torch.utils.data import DataLoader

        if self.custom_dataset_pred:
            if hasattr(self.custom_dataset_pred, "build_dataset") and callable(
                self.custom_dataset_pred.build_dataset
            ):
                self.custom_dataset_train.build_dataset(y)
                dataset = self.custom_dataset_train
            else:
                raise NotImplementedError(
                    "Custom Dataset `build_dataset` method is not available. Please"
                    f"refer to the {self.__class__.__name__}.build_dataset"
                    "documentation."
                )
        else:
            dataset = PyTorchDataset(
                y=y,
                seq_len=self.network.seq_len,
                pred_len=self.network.pred_len,
                scale=self.scale,
            )

        return DataLoader(
            dataset,
            self.batch_size,
            shuffle=self.shuffle,
        )

    def get_y_true(self, y):
        """Get y_true values for validation."""
        dataloader = self.build_pytorch_pred_dataloader(y)
        y_true = [y.flatten().numpy() for _, y in dataloader]
        return np.concatenate(y_true, axis=0)

    def save(self, save_model_path):
        """Save model state dict."""
        from torch import save

        save(self.network.state_dict(), save_model_path)


class PyTorchDataset:
    """Dataset for use in sktime deep learning forecasters."""

    def __init__(self, y, seq_len, pred_len, scale):
        self.y = y
        self.seq_len = seq_len
        self.pred_len = pred_len

        if scale:
            from sklearn.preprocessing import StandardScaler

            self.scaler = StandardScaler()
            self.y = self.scaler.fit_transform(y.values.reshape(-1, 1))
        else:
            self.y = self.y.values

    def __len__(self):
        """Return length of dataset."""
        return len(self.y) - self.seq_len - self.pred_len + 1

    def __getitem__(self, i):
        """Return data point."""
        from torch import from_numpy, tensor

        return (
            tensor(self.y[i : i + self.seq_len]).float(),
            from_numpy(
                self.y[i + self.seq_len : i + self.seq_len + self.pred_len]
            ).float(),
        )

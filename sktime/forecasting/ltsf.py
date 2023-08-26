"""Deep Learning Forecasters using LTSF-Linear Models."""

from sktime.networks.base import BaseDeepNetworkPyTorch
from sktime.networks.ltsf.ltsf import LTSFLinearNetwork


class LTSFLinearForecaster(BaseDeepNetworkPyTorch):
    """LTSF-Linear Forecaster.

    Parameters
    ----------
    seq_len : int
        length of input sequence
    pred_len : int
        length of prediction (forecast horizon)
    lr : float
        learning rate
    num_epochs : int
        number of epochs to train
    batch_size : int
        number of training examples per batch
    in_channels : int, default=None
        number of input channels passed to network
    individual : bool, default=False
        boolean flag that controls whether the network treats each channel individually"
        "or applies a single linear layer across all channels. If individual=True, the"
        "a separate linear layer is created for each input channel. If"
        "individual=False, a single shared linear layer is used for all channels."
    optimizer : torch.optim.Optimizer, default=torch.optim.Adam
        optimizer to be used for training
    criterion : torch.nn Loss Function, default=torch.nn.MSELoss
        loss function to be used for training
    """

    # TODO: fix docstring

    _tags = {
        "scitype:y": "both",
        "y_inner_mtype": "pd.DataFrame",
        "requires-fh-in-fit": False,
        "python_dependencies": "torch",
    }

    def __init__(
        self,
        seq_len,  # L : Historical data
        pred_len,  # T : Future predictions
        *,
        target=None,
        features=None,
        individual=False,
        in_channels=1,
        criterion=None,
        optimizer=None,
        lr=0.001,
        num_epochs=16,
        custom_dataset_train=None,
        custom_dataset_pred=None,
        batch_size=8,
        scale=True,
        shuffle=True,
    ):
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.target = target
        self.features = features
        self.individual = individual
        self.in_channels = in_channels
        self.criterion = criterion
        self.optimizer = optimizer
        self.lr = lr
        self.num_epochs = num_epochs
        self.custom_dataset_train = custom_dataset_train
        self.custom_dataset_pred = custom_dataset_pred
        self.batch_size = batch_size
        self.scale = scale
        self.shuffle = shuffle
        self.network = LTSFLinearNetwork(
            seq_len,
            pred_len,
            in_channels,
            individual,
        )._build()

        import torch

        if self.criterion:
            self._criterion = self.criterion()
        else:
            self._criterion = torch.nn.MSELoss()

        if self.optimizer:
            self._optimizer = self.optimizer(self.network.parameters(), lr=self.lr)
        else:
            self._optimizer = torch.optim.Adam(self.network.parameters(), lr=self.lr)

        super().__init__()

    @classmethod
    def get_test_params(cls, parameter_set="default"):
        """Return testing parameter settings for the estimator.

        Parameters
        ----------
        parameter_set : str, default="default"
            Name of the set of test parameters to return, for use in tests. If no
            special parameters are defined for a value, will return `"default"` set.


        Returns
        -------
        params : dict or list of dict
        """
        import torch

        params = [
            {
                "seq_len": 4,
                "pred_len": 1,
                "lr": 0.005,
                "optimizer": torch.optim.Adam,
                "batch_size": 32,
                "num_epochs": 1,
                "individual": True,
            }
        ]

        return params

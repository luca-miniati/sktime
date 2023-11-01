"""Deep Learning Forecasters using LTSF-Linear Models."""

from sktime.networks.base import BaseDeepNetworkPyTorch


class LTSFLinearForecaster(BaseDeepNetworkPyTorch):
    """LTSF-Linear Forecaster.

    Parameters
    ----------
    seq_len : int
        length of input sequence
    pred_len : int
        length of prediction (forecast horizon)
    num_epochs : int, default=16
        number of epochs to train
    batch_size : int, default=8
        number of training examples per batch
    in_channels : int, default=1
        number of input channels passed to network
    individual : bool, default=False
        boolean flag that controls whether the network treats each channel individually"
        "or applies a single linear layer across all channels. If individual=True, the"
        "a separate linear layer is created for each input channel. If"
        "individual=False, a single shared linear layer is used for all channels."
    criterion : torch.nn Loss Function, default=torch.nn.MSELoss
        loss function to be used for training
    criterion_kwargs : dict, default=None
        keyword arguments to pass to criterion
    optimizer : torch.optim.Optimizer, default=torch.optim.Adam
        optimizer to be used for training
    optimizer_kwargs : dict, default=None
        keyword arguments to pass to optimizer
    lr : float, default=0.003
        learning rate to train model with
    Examples
    --------
    >>> from sktime.forecasting.ltsf import LTSFLinearForecaster # doctest: +SKIP
    >>> from sktime.datasets import load_airline
    >>> model = LTSFLinearForecaster(10, 3) # doctest: +SKIP
    >>> y = load_airline()
    >>> model.fit(y, fh=[1,2,3]) # doctest: +SKIP
    LTSFLinearForecaster(pred_len=3, seq_len=10)
    >>> y_pred = model.predict() # doctest: +SKIP
    >>> y_pred # doctest: +SKIP
    1961-01    515.456726
    1961-02    576.704712
    1961-03    559.859680
    Freq: M, Name: Number of airline passengers, dtype: float32
    """

    def __init__(
        self,
        seq_len,
        pred_len,
        *,
        num_epochs=16,
        batch_size=8,
        in_channels=1,
        individual=False,
        criterion=None,
        criterion_kwargs=None,
        optimizer=None,
        optimizer_kwargs=None,
        lr=0.001,
        custom_dataset_train=None,
        custom_dataset_pred=None,
    ):
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.individual = individual
        self.in_channels = in_channels
        self.criterion = criterion
        self.optimizer = optimizer
        self.criterion_kwargs = criterion_kwargs
        self.optimizer_kwargs = optimizer_kwargs
        self.lr = lr
        self.num_epochs = num_epochs
        self.custom_dataset_train = custom_dataset_train
        self.custom_dataset_pred = custom_dataset_pred
        self.batch_size = batch_size

        super().__init__()

        from sktime.utils.validation._dependencies import _check_soft_dependencies

        if _check_soft_dependencies("torch"):
            import torch

            self.criterions = {
                "MSE": torch.nn.MSELoss,
                "L1": torch.nn.L1Loss,
                "SmoothL1": torch.nn.SmoothL1Loss,
                "Huber": torch.nn.HuberLoss,
            }

            self.optimizers = {
                "Adadelta": torch.optim.Adadelta,
                "Adagrad": torch.optim.Adagrad,
                "Adam": torch.optim.Adam,
                "AdamW": torch.optim.AdamW,
                "SGD": torch.optim.SGD,
            }

    def _build_network(self, fh):
        from sktime.networks.ltsf import LTSFLinearNetwork

        return LTSFLinearNetwork(
            self.seq_len,
            fh,
            self.in_channels,
            self.individual,
        )._build()

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
        params = [
            {
                "seq_len": 2,
                "pred_len": 1,
                "lr": 0.005,
                "optimizer": "Adam",
                "batch_size": 1,
                "num_epochs": 1,
                "individual": True,
            }
        ]

        return params
from settings import FX


class TestFX:


    def test__fx_get__btc_usd(self):

        currency_pair = FX.get("EUR")

        assert "EUR" == currency_pair.get("code")

    def test__fx_get__none(self):

        currency_pair = FX.get("-")

        assert None == currency_pair
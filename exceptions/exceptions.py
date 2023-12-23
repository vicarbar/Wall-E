class StockNotExistsError(Exception):
    pass

class NetworkError(Exception):
    pass

class MatchNoValidError(Exception):
    print("The selected match is not valid. Local team and visitor team can't be the same.")

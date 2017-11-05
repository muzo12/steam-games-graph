from .. import Encoder


def test_two_way_games_translation():
    encoder = Encoder()
    games = [100, 200, 300, 400, 11111, 22222, 12840]

    alpha = encoder.encode_games_array(games)
    print('alpha:', alpha)
    assert alpha

    games_returned = encoder.decode_games_string(alpha)

    assert len(games) == len(games_returned)
    assert games == games_returned

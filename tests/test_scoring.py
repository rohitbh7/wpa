import pytest

from functions.scoring import next_point

P = pytest.param

# Each case: (starting state kwargs for make_row, point winner, expected state)

IN_GAME = [
    P({}, 2, dict(score=('0', '15'), server=1, onehot='game_score_0-15'), id='first_point'),
    P(dict(p1='30', p2='40'), 1, dict(score=('40', '40'), server=1, onehot='game_score_40-40'), id='reach_deuce'),
    P(dict(p1='40', p2='40'), 1, dict(score=('AD', '40'), onehot='game_score_AD-40'), id='deuce_to_ad_p1'),
    P(dict(p1='40', p2='40'), 2, dict(score=('40', 'AD'), onehot='game_score_40-AD'), id='deuce_to_ad_p2'),
    P(dict(p1='AD', p2='40'), 2, dict(score=('40', '40'), onehot='game_score_40-40'), id='ad_lost_p1'),
    P(dict(p1='40', p2='AD'), 1, dict(score=('40', '40'), onehot='game_score_40-40'), id='ad_lost_p2'),
    P(dict(p1='40', p2='30', g1=5, g2=4), 2, dict(score=('40', '40'), games=(5, 4), onehot='game_score_40-40'), id='set_point_saved'),
    P(dict(p1='40', p2='0', g1=5, g2=3, s1=1), 2, dict(score=('40', '15'), games=(5, 3), sets=(1, 0), onehot='game_score_40-15'), id='match_point_saved'),
]

GAME_END = [
    P(dict(p1='AD', p2='40', server=1), 1, dict(score=('0', '0'), games=(1, 0), server=2), id='ad_converted'),
    P(dict(p1='40', p2='AD', server=1), 2, dict(score=('0', '0'), games=(0, 1), server=2), id='receiver_ad_break'),
    P(dict(p1='40', p2='15', g1=2, g2=2, server=1), 1, dict(score=('0', '0'), games=(3, 2), server=2), id='game_point_hold'),
    P(dict(p1='30', p2='40', g1=2, g2=2, server=1), 2, dict(score=('0', '0'), games=(2, 3), server=2), id='break_point'),
    P(dict(p1='40', p2='0'), 1, dict(score=('0', '0'), games=(1, 0), server=2), id='love_game'),
]

SET_END = [
    P(dict(p1='40', p2='30', g1=5, g2=4, server=1), 1, dict(score=('0', '0'), sets=(1, 0), server=2), id='set_6_4'),
    P(dict(p1='40', p2='30', g1=5, g2=5), 1, dict(score=('0', '0'), games=(6, 5)), id='no_set_at_6_5'),
    P(dict(p1='40', p2='30', g1=6, g2=5), 1, dict(score=('0', '0'), sets=(1, 0)), id='set_7_5'),
    P(dict(p1='40', p2='30', g1=5, g2=6, server=1), 1, dict(score=('0', '0'), games=(6, 6), server=2, tb=True), id='force_tiebreak'),
]

TB = dict(g1=6, g2=6, tb=True)

TIEBREAK_POINTS = [
    P(dict(p1='0', p2='0', server=1, **TB), 1, dict(score=('1', '0'), games=(6, 6), server=2, tb=True), id='first_point_switch'),
    P(dict(p1='1', p2='0', server=2, **TB), 2, dict(score=('1', '1'), games=(6, 6), server=2, tb=True), id='second_point_no_switch'),
    P(dict(p1='1', p2='1', server=2, **TB), 1, dict(score=('2', '1'), games=(6, 6), server=1, tb=True), id='third_point_switch'),
    P(dict(p1='6', p2='5', server=1, **TB), 2, dict(score=('6', '6'), games=(6, 6), server=1, tb=True), id='set_point_saved'),
    P(dict(p1='6', p2='6', server=1, **TB), 1, dict(score=('7', '6'), games=(6, 6), server=2, tb=True), id='7_6_not_over'),
]

# Next-set server = whoever received first in the tiebreak.
TIEBREAK_END = [
    P(dict(p1='6', p2='5', server=1, **TB), 1, dict(score=('0', '0'), sets=(1, 0), server=2), id='7_5_p1'),
    P(dict(p1='5', p2='6', server=2, **TB), 2, dict(score=('0', '0'), sets=(0, 1), server=1), id='7_5_p2'),
    P(dict(p1='6', p2='4', server=1, **TB), 1, dict(score=('0', '0'), sets=(1, 0), server=1), id='7_4_other_rotation'),
    P(dict(p1='9', p2='8', server=2, **TB), 1, dict(score=('0', '0'), sets=(1, 0), server=2), id='extended_10_8'),
]

MATCH_END = [
    P(dict(p1='40', p2='0', g1=5, g2=3, s1=1), 1, dict(score=('0', '0'), sets=(2, 0)), id='bo3_straight_sets'),
    P(dict(p1='6', p2='5', s1=1, s2=1, server=1, **TB), 1, dict(score=('0', '0'), sets=(2, 1)), id='bo3_third_set_tiebreak'),
    P(dict(p1='40', p2='AD', g1=4, g2=5, s1=2, s2=2, best_of=5), 2, dict(score=('0', '0'), sets=(2, 3)), id='bo5_fifth_set_break'),
]


@pytest.mark.parametrize('start, winner, expected', IN_GAME)
def test_in_game_points(make_row, expect, start, winner, expected):
    expect(next_point(make_row(**start), winner), **expected)


@pytest.mark.parametrize('start, winner, expected', GAME_END)
def test_game_endings(make_row, expect, start, winner, expected):
    expect(next_point(make_row(**start), winner), **expected)


@pytest.mark.parametrize('start, winner, expected', SET_END)
def test_set_endings(make_row, expect, start, winner, expected):
    expect(next_point(make_row(**start), winner), **expected)


@pytest.mark.parametrize('start, winner, expected', TIEBREAK_POINTS)
def test_tiebreak_points(make_row, expect, start, winner, expected):
    expect(next_point(make_row(**start), winner), **expected)


@pytest.mark.parametrize('start, winner, expected', TIEBREAK_END)
def test_tiebreak_endings(make_row, expect, start, winner, expected):
    expect(next_point(make_row(**start), winner), **expected)


@pytest.mark.parametrize('start, winner, expected', MATCH_END)
def test_match_endings(make_row, expect, start, winner, expected):
    out = next_point(make_row(**start), winner)
    expect(out, **expected)
    r = out.iloc[0]
    assert max(r['P1SetsWon'], r['P2SetsWon']) > r['BestOf'] // 2


# ---------- final-set 10-point tiebreak ----------

def test_10pt_tiebreak_not_over_at_7(make_row, expect):
    row = make_row('6', '4', s1=2, s2=2, server=1, best_of=5, **TB)
    expect(next_point(row, 1, tb_target=10), ('7', '4'), games=(6, 6), sets=(2, 2), tb=True)


def test_10pt_tiebreak_match_point(make_row, expect):
    row = make_row('9', '7', s1=2, s2=2, server=1, best_of=5, **TB)
    expect(next_point(row, 1, tb_target=10), ('0', '0'), sets=(3, 2))


# ---------- sequences ----------

def test_tiebreak_serve_rotation(make_row):
    """Server pattern in a tiebreak: A, B, B, A, A, B, B, A, A, B."""
    row = make_row('0', '0', server=1, **TB)
    servers = []
    for i in range(10):
        servers.append(int(row.iloc[0]['PointServer']))
        row = next_point(row, 1 if i % 2 == 0 else 2)  # alternate so nobody wins
    assert servers == [1, 2, 2, 1, 1, 2, 2, 1, 1, 2]


def test_love_hold_chain(make_row, expect):
    row = make_row(server=1)
    for _ in range(4):
        row = next_point(row, 1)
    expect(row, ('0', '0'), games=(1, 0), server=2)


def test_deuce_battle_chain(make_row, expect):
    row = make_row('40', '40')
    for w in [1, 2, 2, 1, 1, 1]:  # AD-40, 40-40, 40-AD, 40-40, AD-40, game
        row = next_point(row, w)
    expect(row, ('0', '0'), games=(1, 0))


# ---------- plumbing ----------

def test_input_not_mutated(make_row):
    row = make_row('40', '40')
    before = row.copy()
    next_point(row, 1)
    assert row.equals(before)


def test_shape_and_passthrough_columns(make_row, columns):
    row = make_row('AD', '40', best_of=5)
    out = next_point(row, 1)
    assert out.shape == (1, len(columns))
    assert list(out.columns) == columns
    for c in ['match_id', 'player1', 'player2', 'BestOf', 'MatchWinner']:
        assert out.iloc[0][c] == row.iloc[0][c]


@pytest.mark.parametrize('winner', [0, 3, '1', None])
def test_invalid_winner_raises(make_row, winner):
    with pytest.raises(ValueError):
        next_point(make_row(), winner)


def test_multi_row_input_raises(make_row):
    import pandas as pd
    two_rows = pd.concat([make_row(), make_row()])
    with pytest.raises(ValueError):
        next_point(two_rows, 1)
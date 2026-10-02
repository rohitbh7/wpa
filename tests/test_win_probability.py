import pandas as pd
import pytest

from functions.win_probability import win_probabilities


def test_shape_and_scenarios(make_row):
    out = win_probabilities(make_row())
    assert list(out['scenario']) == ['current', 'p1_wins_point', 'p2_wins_point']
    assert out.shape == (3, 4)


def test_probabilities_complementary(make_row):
    out = win_probabilities(make_row())
    for _, r in out.iterrows():
        assert r['p1_win_prob'] + r['p2_win_prob'] == 1


def test_winning_point_raises_p1_win_prob(make_row):
    out = win_probabilities(make_row('30', '30')).set_index('scenario')
    current = out.loc['current', 'p1_win_prob']
    assert out.loc['p1_wins_point', 'p1_win_prob'] > current
    assert out.loc['p2_wins_point', 'p1_win_prob'] < current


def test_scores_match_next_point_outcomes(make_row):
    out = win_probabilities(make_row()).set_index('scenario')
    assert out.loc['current', 'score'] == '0-0; 0-0; 0-0'
    assert out.loc['p1_wins_point', 'score'] == '0-0; 0-0; 15-0'
    assert out.loc['p2_wins_point', 'score'] == '0-0; 0-0; 0-15'


def test_multi_row_input_raises(make_row):
    two_rows = pd.concat([make_row(), make_row()])
    with pytest.raises(ValueError):
        win_probabilities(two_rows)

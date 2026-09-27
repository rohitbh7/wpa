import pandas as pd
import pytest

COLUMNS = ['match_id', 'player1', 'player2', 'PointServer',
           'P1SetsWon', 'P2SetsWon', 'P1GamesWon', 'P2GamesWon', 'IsTiebreak',
           'P1Score', 'P2Score', 'BestOf', 'MatchWinner', 'game_score_0-15',
           'game_score_0-30', 'game_score_0-40', 'game_score_15-0',
           'game_score_15-15', 'game_score_15-30', 'game_score_15-40',
           'game_score_30-0', 'game_score_30-15', 'game_score_30-30',
           'game_score_30-40', 'game_score_40-0', 'game_score_40-15',
           'game_score_40-30', 'game_score_40-40', 'game_score_40-AD',
           'game_score_AD-40']
SCORE_COLS = [c for c in COLUMNS if c.startswith('game_score_')]


@pytest.fixture
def columns():
    return COLUMNS


@pytest.fixture
def make_row():
    """Build a one-row state DataFrame with sensible defaults."""
    def _make(p1='0', p2='0', g1=0, g2=0, s1=0, s2=0, server=1, tb=False, best_of=3):
        row = {'match_id': 'test', 'player1': 'A', 'player2': 'B',
               'PointServer': server,
               'P1SetsWon': s1, 'P2SetsWon': s2,
               'P1GamesWon': g1, 'P2GamesWon': g2,
               'IsTiebreak': tb, 'P1Score': p1, 'P2Score': p2,
               'BestOf': best_of, 'MatchWinner': 1}
        for c in SCORE_COLS:
            row[c] = 0
        key = f'game_score_{p1}-{p2}'
        if not tb and key in row:
            row[key] = 1
        return pd.DataFrame([row])[COLUMNS]
    return _make


@pytest.fixture
def expect():
    """Assert on the state of a one-row output DataFrame."""
    def _expect(out, score, games=(0, 0), sets=(0, 0), server=None, tb=False, onehot=None):
        r = out.iloc[0]
        assert (r['P1Score'], r['P2Score']) == score
        assert (r['P1GamesWon'], r['P2GamesWon']) == games
        assert (r['P1SetsWon'], r['P2SetsWon']) == sets
        if server is not None:
            assert r['PointServer'] == server
        assert bool(r['IsTiebreak']) == tb
        hot = [c for c in SCORE_COLS if r[c] == 1]
        assert hot == ([onehot] if onehot else [])
    return _expect
import pandas as pd

LABELS = ['0', '15', '30', '40']
TO_COUNT = {'0': 0, '15': 1, '30': 2, '40': 3, 'AD': 4}

def _game_label(a, b):
    """Point counts -> display scores (handles deuce/advantage)."""
    if a >= 3 and b >= 3:
        if a == b:
            return '40', '40'
        return ('AD', '40') if a > b else ('40', 'AD')
    return LABELS[a], LABELS[b]

def next_point(row_df, winner, tb_target=7):
    if winner not in (1, 2):
        raise ValueError(f"winner must be 1 or 2, got {winner!r}")
    if len(row_df) != 1:
        raise ValueError(f"row_df must have exactly one row, got {len(row_df)}")

    new = row_df.copy()
    idx = new.index[0]
    r = new.iloc[0]
    score_cols = [c for c in new.columns if c.startswith('game_score_')]

    tb = bool(r['IsTiebreak'])
    server = int(r['PointServer'])
    games = [int(r['P1GamesWon']), int(r['P2GamesWon'])]
    sets = [int(r['P1SetsWon']), int(r['P2SetsWon'])]
    if tb:
        pts = [int(r['P1Score']), int(r['P2Score'])]
    else:
        pts = [TO_COUNT[str(r['P1Score'])], TO_COUNT[str(r['P2Score'])]]

    before = sum(pts)          # points already played in this game/tiebreak
    w = winner - 1
    pts[w] += 1

    target = tb_target if tb else 4
    game_over = pts[w] >= target and pts[w] - pts[1 - w] >= 2

    if not game_over:
        # tiebreak: serve changes after point 1, then every 2 points
        if tb and sum(pts) % 2 == 1:
            server = 3 - server
    else:
        games[w] += 1
        pts = [0, 0]
        if tb:
            # whoever served first in the tiebreak receives first next set
            first_tb_server = server if ((before + 1) // 2) % 2 == 0 else 3 - server
            server = 3 - first_tb_server
        else:
            server = 3 - server

        set_over = tb or (games[w] >= 6 and games[w] - games[1 - w] >= 2)
        if set_over:
            sets[w] += 1
            games = [0, 0]
            # match is over if sets[w] > r['BestOf'] // 2
        tb = games == [6, 6]

    s1, s2 = (str(pts[0]), str(pts[1])) if tb else _game_label(*pts)

    new.loc[idx, ['P1Score', 'P2Score']] = [s1, s2]
    new.loc[idx, ['P1GamesWon', 'P2GamesWon']] = games
    new.loc[idx, ['P1SetsWon', 'P2SetsWon']] = sets
    new.loc[idx, 'PointServer'] = server
    new.loc[idx, 'IsTiebreak'] = type(r['IsTiebreak'])(tb)

    # rebuild the one-hot game score (0-0 and tiebreaks have no column)
    new[score_cols] = 0
    col = f'game_score_{s1}-{s2}'
    if not tb and col in new.columns:
        new.loc[idx, col] = 1

    return new
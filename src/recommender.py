from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# ---------------------------------------------------------------------------
# Scoring modes — Strategy pattern
#
# Each mode is a config dict that controls how the four base signals are
# weighted.  Pass the mode name to score_song() or recommend_songs() and
# the scorer will use that config automatically.
#
# Keys
#   genre_pts   — fixed points awarded for an exact genre match
#   mood_pts    — fixed points awarded for an exact mood match
#   energy_mult — multiplier applied to the raw energy-closeness value (0–1)
#   tempo_mult  — multiplier applied to the raw tempo-closeness value  (0–1)
# ---------------------------------------------------------------------------
SCORING_MODES: Dict[str, Dict[str, float]] = {
    # Genre-First: genre is the dominant signal.
    # Best for users who know exactly what genre they want and rarely stray.
    # Max base score = 3.0 + 0.5 + 1.0 + 0.5 = 5.0
    "genre_first": {
        "genre_pts":   3.0,
        "mood_pts":    0.5,
        "energy_mult": 1.0,
        "tempo_mult":  0.5,
    },

    # Mood-First: emotional tone / vibe is the dominant signal.
    # Best for users who care more about how a song feels than what genre it is.
    # Max base score = 0.5 + 3.0 + 1.0 + 0.5 = 5.0
    "mood_first": {
        "genre_pts":   0.5,
        "mood_pts":    3.0,
        "energy_mult": 1.0,
        "tempo_mult":  0.5,
    },

    # Energy-Focused: continuous signals (energy + tempo) dominate.
    # Best for workout or focus playlists where intensity/BPM matters most.
    # Max base score = 0.5 + 0.5 + 2.0 + 1.5 = 4.5
    "energy_focused": {
        "genre_pts":   0.5,
        "mood_pts":    0.5,
        "energy_mult": 2.0,
        "tempo_mult":  1.5,
    },
}

DEFAULT_MODE = "genre_first"

TEMPO_RANGE = 100.0  # BPM window used to normalise tempo distance

# ---------------------------------------------------------------------------
# Diversity penalty values (Challenge 3)
#
# Applied during greedy selection when a song's artist or genre is already
# represented in the results built so far.  Penalties reduce the effective
# score for that slot only — the song's base score is never changed.
#
#   ARTIST_PENALTY  prevents the same artist appearing twice in the top k
#   GENRE_PENALTY   discourages back-to-back songs from the same genre
# ---------------------------------------------------------------------------
ARTIST_PENALTY = 1.0   # deducted when artist already in selected results
GENRE_PENALTY  = 0.5   # deducted when genre already in selected results


@dataclass
class Song:
    """Represents a song and its attributes. Required by tests/test_recommender.py"""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float
    liveness: float
    # Advanced features (Challenge 1)
    popularity: int        # 0–100 chart/stream popularity
    release_decade: int    # e.g. 1990, 2000, 2010, 2020
    detailed_mood: str     # finer mood tag: euphoric, dreamy, aggressive, nostalgic, etc.
    speechiness: float     # 0.0–1.0; high values indicate rap/spoken-word content
    mode: int              # 1 = major key (brighter), 0 = minor key (darker)


@dataclass
class UserProfile:
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    likes_instrumental: bool
    target_tempo: float = 100.0
    # Advanced preferences (Challenge 1) — all optional, default to None / False
    target_popularity: Optional[float] = None  # 0–100; score songs near this popularity
    preferred_decade: Optional[int] = None     # e.g. 2020; reward era-matching songs
    preferred_detailed_mood: Optional[str] = None  # e.g. "euphoric"; exact tag match
    likes_speech: bool = False                 # reward high-speechiness (rap/spoken word)
    prefers_major: Optional[bool] = None       # True=major, False=minor, None=no pref


def _explain_song(song: Song, user: UserProfile) -> str:
    """Builds a human-readable explanation for why a song was recommended."""
    reasons = []

    if song.genre == user.favorite_genre:
        reasons.append(f"genre matches your preference ({song.genre})")
    if song.mood == user.favorite_mood:
        reasons.append(f"mood matches ({song.mood})")

    energy_diff = abs(song.energy - user.target_energy)
    if energy_diff <= 0.15:
        reasons.append(f"energy is close to your target ({song.energy:.2f})")

    if not reasons:
        reasons.append("best available match given your preferences")

    return "Recommended because: " + "; ".join(reasons) + "."


class Recommender:
    """OOP wrapper around score_song and recommend_songs. Required by tests/test_recommender.py"""

    def __init__(self, songs: List[Song]):
        """Store the song catalog that this recommender will rank against."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, mode: str = DEFAULT_MODE) -> List[Song]:
        """Return the top k Song objects ranked by score for the given user profile."""
        scored = sorted(
            self.songs,
            key=lambda s: score_song(vars(user), vars(s), mode)[0],
            reverse=True,
        )
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-English string explaining why a song was recommended to this user."""
        return _explain_song(song, user)


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with text fields as strings and numeric fields converted to int or float."""
    songs = []  # start with an empty list; we'll add one song per row

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # reads the header row automatically

        for row in reader:
            # CSV files store everything as text, so we convert numbers explicitly.
            song = {
                "id":               int(row["id"]),
                "title":            row["title"],        # string — keep as-is
                "artist":           row["artist"],       # string — keep as-is
                "genre":            row["genre"],        # string — keep as-is
                "mood":             row["mood"],         # string — keep as-is
                "energy":           float(row["energy"]),           # 0.0 – 1.0
                "tempo_bpm":        int(row["tempo_bpm"]),          # e.g. 120
                "valence":          float(row["valence"]),          # 0.0 – 1.0
                "danceability":     float(row["danceability"]),     # 0.0 – 1.0
                "acousticness":     float(row["acousticness"]),     # 0.0 – 1.0
                "instrumentalness": float(row["instrumentalness"]), # 0.0 – 1.0
                "liveness":         float(row["liveness"]),         # 0.0 – 1.0
                # Advanced features (Challenge 1)
                "popularity":       int(row["popularity"]),         # 0–100
                "release_decade":   int(row["release_decade"]),     # e.g. 2020
                "detailed_mood":    row["detailed_mood"],           # string tag
                "speechiness":      float(row["speechiness"]),      # 0.0–1.0
                "mode":             int(row["mode"]),               # 1=major, 0=minor
            }
            songs.append(song)

    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """Score a song against user preferences using the given scoring mode.

    Modes (defined in SCORING_MODES) control how much weight each base signal
    receives.  All bonus signals (acoustic, instrumental, popularity, etc.) are
    mode-independent and always added on top of the base score.

    Returns (total_score, reasons) where reasons is a list of human-readable strings.
    """
    cfg = SCORING_MODES[mode]
    total_score = 0.0
    reasons = []

    # Genre match — fixed points from the mode config
    if song["genre"] == user_prefs["favorite_genre"]:
        pts = cfg["genre_pts"]
        total_score += pts
        reasons.append(f"genre match (+{pts:.1f})")

    # Mood match — fixed points from the mode config
    if song["mood"] == user_prefs["favorite_mood"]:
        pts = cfg["mood_pts"]
        total_score += pts
        reasons.append(f"mood match (+{pts:.1f})")

    # Energy similarity — raw closeness (0–1) scaled by the mode multiplier
    # max(0.0, ...) ensures we never subtract points for a poor energy fit
    raw_energy = max(0.0, 1.0 - abs(song["energy"] - user_prefs["target_energy"]))
    energy_points = raw_energy * cfg["energy_mult"]
    total_score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.1f})")

    # Tempo similarity — raw closeness (0–1) scaled by the mode multiplier
    if "target_tempo" in user_prefs:
        raw_tempo = max(0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs["target_tempo"]) / TEMPO_RANGE)
        tempo_points = raw_tempo * cfg["tempo_mult"]
        total_score += tempo_points
        reasons.append(f"tempo similarity (+{tempo_points:.1f})")

    # +0.5 bonus if the user likes acoustic songs and this song is highly acoustic (optional)
    if user_prefs.get("likes_acoustic") and song.get("acousticness", 0.0) > 0.7:
        total_score += 0.5
        reasons.append(f"acoustic bonus (+0.5, acousticness={song['acousticness']:.2f})")

    # +0.5 bonus if the user likes instrumental songs and this song is predominantly instrumental (optional)
    if user_prefs.get("likes_instrumental") and song.get("instrumentalness", 0.0) > 0.6:
        total_score += 0.5
        reasons.append(f"instrumental bonus (+0.5, instrumentalness={song['instrumentalness']:.2f})")

    # ------------------------------------------------------------------ Advanced scoring (Challenge 1)

    # Popularity: +0.0–0.5 based on closeness to the user's target popularity (0–100).
    # Normalized over a 50-point window — a gap of 50+ earns 0 points.
    # Formula: max(0, 1 - |song_pop - target_pop| / 50) * 0.5
    if user_prefs.get("target_popularity") is not None:
        pop_gap = abs(song.get("popularity", 50) - user_prefs["target_popularity"])
        pop_points = max(0.0, 1.0 - pop_gap / 50.0) * 0.5
        total_score += pop_points
        reasons.append(f"popularity match (+{pop_points:.2f}, popularity={song.get('popularity', '?')})")

    # Decade: +0.0–0.5 based on how close the song's release decade is to the user's preference.
    # Normalized over 30 years (3 decades) — a gap of 30+ years earns 0 points.
    # Formula: max(0, 1 - |song_decade - target_decade| / 30) * 0.5
    if user_prefs.get("preferred_decade") is not None:
        decade_gap = abs(song.get("release_decade", 2000) - user_prefs["preferred_decade"])
        decade_points = max(0.0, 1.0 - decade_gap / 30.0) * 0.5
        total_score += decade_points
        reasons.append(f"era match (+{decade_points:.2f}, decade={song.get('release_decade', '?')})")

    # Detailed mood: +0.75 for an exact tag match (e.g. "euphoric", "dreamy", "aggressive").
    # Worth more than acoustic/instrumental bonuses but less than the main mood signal.
    if user_prefs.get("preferred_detailed_mood") and \
            song.get("detailed_mood") == user_prefs["preferred_detailed_mood"]:
        total_score += 0.75
        reasons.append(f"detailed mood match (+0.75, tag={song['detailed_mood']})")

    # Speechiness: +0.5 bonus if the user likes rap/spoken-word and this song is speech-heavy.
    # Threshold > 0.3 filters out songs that are mostly sung (typical value for rap is 0.33+).
    if user_prefs.get("likes_speech") and song.get("speechiness", 0.0) > 0.3:
        total_score += 0.5
        reasons.append(f"speechiness bonus (+0.5, speechiness={song['speechiness']:.2f})")

    # Mode (key): +0.25 if the song's key type matches the user's tonal preference.
    # Major (mode=1) sounds brighter/happier; minor (mode=0) sounds darker/more emotional.
    if user_prefs.get("prefers_major") is True and song.get("mode") == 1:
        total_score += 0.25
        reasons.append("major key match (+0.25)")
    elif user_prefs.get("prefers_major") is False and song.get("mode") == 0:
        total_score += 0.25
        reasons.append("minor key match (+0.25)")

    return total_score, reasons


def _select_diverse(
    scored: List[Tuple[Dict, float, List[str]]], k: int
) -> List[Tuple[Dict, float, List[str]]]:
    """Greedy diversity-aware selection (Challenge 3).

    Works on the pre-sorted list of (song, base_score, reasons_list) tuples.
    At each slot it re-evaluates every remaining song with penalties applied
    for artist/genre overlap with songs already selected, then picks the best.

    Penalties are noted in the reasons list so they appear in the final output.
    The song's base score is never modified — only the effective score used for
    this selection step is adjusted.
    """
    selected: List[Tuple[Dict, float, List[str]]] = []
    seen_artists: set = set()
    seen_genres:  set = set()
    remaining = list(scored)   # shallow copy; base scores stay unchanged

    while len(selected) < k and remaining:
        best_idx       = 0
        best_eff_score = float("-inf")
        best_reasons:  List[str] = []

        for i, (song, base_score, reasons) in enumerate(remaining):
            eff_score     = base_score
            extra_reasons = list(reasons)   # copy so we don't mutate the original

            if song["artist"] in seen_artists:
                eff_score -= ARTIST_PENALTY
                extra_reasons.append(f"artist diversity penalty (-{ARTIST_PENALTY:.1f})")
            if song["genre"] in seen_genres:
                eff_score -= GENRE_PENALTY
                extra_reasons.append(f"genre diversity penalty (-{GENRE_PENALTY:.1f})")

            if eff_score > best_eff_score:
                best_eff_score = eff_score
                best_idx       = i
                best_reasons   = extra_reasons

        chosen_song, _, _ = remaining.pop(best_idx)
        seen_artists.add(chosen_song["artist"])
        seen_genres.add(chosen_song["genre"])
        selected.append((chosen_song, best_eff_score, best_reasons))

    return selected


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = DEFAULT_MODE,
                    diversity: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score every song using the given mode, sort descending, and return the top k.

    mode      — one of the keys in SCORING_MODES (default: DEFAULT_MODE)
    diversity — when True, applies artist/genre diversity penalties during
                selection so the top k spans more artists and genres

    Each item in the returned list is (song_dict, score, explanation_string).
    """
    # Step 1: score every song and keep the raw reasons list for now
    scored: List[Tuple[Dict, float, List[str]]] = []
    for song in songs:
        total_score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, total_score, reasons))

    # Step 2: sort by base score descending
    scored = sorted(scored, key=lambda e: e[1], reverse=True)

    # Step 3: select top k — plain slice or diversity-penalised greedy pick
    top_k = _select_diverse(scored, k) if diversity else scored[:k]

    # Step 4: join reason lists into explanation strings and return
    return [
        (song, score, "Recommended because: " + "; ".join(reasons) + ".")
        for song, score, reasons in top_k
    ]

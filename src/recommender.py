from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# ---------------------------------------------------------------------------
# Scoring weights — adjust these to tune recommendation behavior
# ---------------------------------------------------------------------------
WEIGHT_GENRE  = 3.0   # genre is the strongest long-term taste signal
WEIGHT_MOOD   = 2.0   # mood is strong but more contextual
WEIGHT_ENERGY = 1.5   # wide range (0–1), good discriminator
WEIGHT_TEMPO  = 0.5   # correlated with energy; smaller independent value
MAX_SCORE     = WEIGHT_GENRE + WEIGHT_MOOD + WEIGHT_ENERGY + WEIGHT_TEMPO  # 7.0
TEMPO_RANGE   = 100.0 # BPM window used to normalize tempo distance


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


@dataclass
class UserProfile:
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    likes_instrumental: bool
    target_tempo: float = 100.0


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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects ranked by score for the given user profile."""
        scored = sorted(
            self.songs,
            key=lambda s: score_song(vars(user), vars(s))[0],
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
            }
            songs.append(song)

    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences and return (total_score, reasons) with points for genre, mood, energy, tempo, and optional acoustic/instrumental bonuses."""
    total_score = 0.0
    reasons = []

    # +2.0 for an exact genre match
    if song["genre"] == user_prefs["favorite_genre"]:
        total_score += 2.0
        reasons.append("genre match (+2.0)")

    # +1.0 for an exact mood match
    if song["mood"] == user_prefs["favorite_mood"]:
        total_score += 1.0
        reasons.append("mood match (+1.0)")

    # +0.0–1.0 based on how close the song's energy is to the user's target
    # max(0.0, ...) ensures we never subtract points for a bad energy fit
    energy_points = max(0.0, 1.0 - abs(song["energy"] - user_prefs["target_energy"]))
    total_score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.1f})")

    # +0.0–1.0 based on tempo closeness, normalized over TEMPO_RANGE (optional)
    if "target_tempo" in user_prefs:
        tempo_points = max(0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs["target_tempo"]) / TEMPO_RANGE)
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

    return total_score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, and return the top k as (song, score, explanation) tuples."""
    # Score every song in the catalog using score_song as the judge
    scored = []
    for song in songs:
        total_score, reasons = score_song(user_prefs, song)
        scored.append((song, total_score, reasons))

    # sorted() returns a new list — safer than .sort() which mutates the original
    scored = sorted(scored, key=lambda entry: entry[1], reverse=True)

    # Format reasons into a single explanation string and return the top k
    return [
        (song, total_score, "Recommended because: " + "; ".join(reasons) + ".")
        for song, total_score, reasons in scored[:k]
    ]

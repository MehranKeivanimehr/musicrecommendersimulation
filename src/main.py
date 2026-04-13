"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from tabulate import tabulate

try:
    from recommender import load_songs, recommend_songs, DEFAULT_MODE   # python src/main.py
except ImportError:
    from src.recommender import load_songs, recommend_songs, DEFAULT_MODE  # python -m src.main


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    # Each profile includes a "scoring_mode" key that selects which ranking
    # strategy to use.  Remove the key before passing prefs to recommend_songs
    # so the scorer never sees an unexpected field.
    profiles = {
    "High-Energy Pop": {
        "scoring_mode":            "genre_first",   # user knows exactly what genre they want
        "favorite_genre":          "pop",
        "favorite_mood":           "happy",
        "target_energy":           0.85,
        "target_tempo":            125,
        "likes_acoustic":          False,
        "likes_instrumental":      False,
        "target_popularity":       80,
        "preferred_detailed_mood": "euphoric",
        "prefers_major":           True,
    },
    "Chill Lofi": {
        "scoring_mode":            "mood_first",    # vibe matters more than strict genre label
        "favorite_genre":          "lofi",
        "favorite_mood":           "chill",
        "target_energy":           0.30,
        "target_tempo":            80,
        "likes_acoustic":          True,
        "likes_instrumental":      True,
        "preferred_decade":        2020,
        "preferred_detailed_mood": "dreamy",
        "prefers_major":           False,
    },
    "Deep Intense Rock": {
        "scoring_mode":            "energy_focused", # intensity/BPM is the primary driver
        "favorite_genre":          "rock",
        "favorite_mood":           "intense",
        "target_energy":           0.90,
        "target_tempo":            140,
        "likes_acoustic":          False,
        "likes_instrumental":      False,
        "preferred_detailed_mood": "aggressive",
        "prefers_major":           False,
        "target_popularity":       30,
    },
    }

    for profile_name, prefs in profiles.items():
        # Pull the mode out before scoring — recommend_songs doesn't expect it
        mode = prefs.pop("scoring_mode", DEFAULT_MODE)
        recommendations = recommend_songs(prefs, songs, k=5, mode=mode, diversity=True)

        # ------------------------------------------------------------------ header
        print("\n" + "=" * 68)
        print(f"  {profile_name}  |  mode: {mode}  |  diversity: ON")
        print(f"  genre: {prefs['favorite_genre']}  |  "
              f"mood: {prefs['favorite_mood']}  |  "
              f"energy: {prefs['target_energy']}")
        print("=" * 68)

        # ----------------------------------------------------------------- table
        rows = []
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            reasons_text = explanation.replace("Recommended because: ", "").rstrip(".")
            reasons_bullets = "\n".join(f"• {r}" for r in reasons_text.split("; "))
            rows.append([
                rank,
                song["title"],
                song["artist"],
                song["genre"],
                f"{score:.2f}",
                reasons_bullets,
            ])

        print(tabulate(
            rows,
            headers=["#", "Title", "Artist", "Genre", "Score", "Reasons"],
            tablefmt="grid",
            colalign=("center", "left", "left", "left", "right", "left"),
        ))
        print()


if __name__ == "__main__":
    main()

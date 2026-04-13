"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

try:
    from recommender import load_songs, recommend_songs   # python src/main.py
except ImportError:
    from src.recommender import load_songs, recommend_songs  # python -m src.main


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = {
        "favorite_genre":     "pop",
        "favorite_mood":      "happy",
        "target_energy":      0.80,
        "target_tempo":       120,
        "likes_acoustic":     False,
        "likes_instrumental": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # ------------------------------------------------------------------ header
    print("=" * 52)
    print("  Top Recommendations for your profile")
    print(f"  Genre: {user_prefs['favorite_genre']}  |  "
          f"Mood: {user_prefs['favorite_mood']}  |  "
          f"Energy: {user_prefs['target_energy']}")
    print("=" * 52)

    # ----------------------------------------------------------------- results
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  ({song['artist']})")
        print(f"    Score : {score:.2f}")

        # explanation is "Recommended because: reason1; reason2; ..."
        # strip the prefix so we can bullet each reason individually
        reasons_text = explanation.replace("Recommended because: ", "").rstrip(".")
        for reason in reasons_text.split("; "):
            print(f"    - {reason}")

    print("\n" + "=" * 52)


if __name__ == "__main__":
    main()

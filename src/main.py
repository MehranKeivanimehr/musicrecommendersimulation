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

    profiles = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "target_tempo": 125,
        "likes_acoustic": False,
        "likes_instrumental": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.30,
        "target_tempo": 80,
        "likes_acoustic": True,
        "likes_instrumental": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "target_tempo": 140,
        "likes_acoustic": False,
        "likes_instrumental": False,
    },
    }



    for profile_name, user_prefs in profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        # ------------------------------------------------------------------ header
        print("=" * 52)
        print(f"  Top Recommendations for: {profile_name}")
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

        print("=" * 52 + "\n")


if __name__ == "__main__":
    main()

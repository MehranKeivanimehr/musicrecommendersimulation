# Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder suggests songs from a small catalog based on what a user tells it they like. You give it your favorite genre, mood, and energy level, and it returns the five songs that match best. The goal is to show how a real recommender system works in a simple, transparent way — every score can be explained in plain English.

---

## 3. Data Used

The catalog has 18 songs. Each song has a genre, a mood, an energy level (0 to 1), and a tempo in BPM. Songs also have acousticness and instrumentalness values, which affect scoring if the user says they like those qualities.

The catalog covers 15 different genres, but most genres only have one song. Lofi has three songs. Pop has two. Everything else — rock, jazz, blues, metal, country, classical — has exactly one. This means the system works well for lofi fans and starts struggling for anyone who wants something more niche.

Moods are things like happy, chill, intense, sad, nostalgic, and romantic. About half the moods appear only once. Energy ranges from 0.22 (very calm) to 0.96 (very intense), with most songs leaning toward the higher end.

---

## 4. Algorithm Summary

For each song in the catalog, the system gives it a score based on how well it matches the user's preferences. Higher score means better match. The five highest-scoring songs are returned as recommendations.

Here is how the score is built:

- **Genre match:** If the song's genre matches what the user likes, it gets 2 points. This is the biggest single factor.
- **Mood match:** If the mood matches (for example, both are "happy"), it gets 1 point.
- **Energy similarity:** The closer the song's energy is to the user's target, the more points it earns — up to 1 point for a perfect match.
- **Tempo similarity:** Same idea as energy, but for beats per minute — up to 1 point.
- **Acoustic bonus:** If the user likes acoustic songs and this song is very acoustic, it gets an extra 0.5 points.
- **Instrumental bonus:** Same for instrumental preference — up to 0.5 extra points.

The maximum possible score is 6 points. A song that matches genre, mood, energy, and tempo perfectly — and fires both bonuses — hits that ceiling.

---

## 5. Observed Behavior / Biases

**Genre dominates everything.** Getting a genre match is worth 2 points, which is more than a perfect energy match and a perfect mood match combined. This means a song in the right genre but the wrong mood will almost always beat a song in the wrong genre but the right mood. For example, Gym Hero — a loud workout song — ranks above better mood matches for a "happy pop" user, just because it has the pop genre tag.

**The system has no way to see related genres.** "Indie pop" and "pop" are completely different in the system's eyes. If you ask for pop, a song labeled "indie pop" gets zero genre points, even if a human listener would consider it basically the same thing.

**When there is only one song in a genre, the system quietly fails.** The rock profile got Storm Runner at #1 — a perfect match — and then four non-rock songs for the remaining spots. The system showed all five results the same way, with no warning that most of them were not what the user asked for.

**Low-energy users get fewer good options.** Only 5 out of 18 songs have an energy below 0.4. If you want calm music, the catalog does not have much to offer outside of the lofi section.

---

## 6. Evaluation Process

Three profiles were tested:

- **High-Energy Pop** (pop, happy, energy 0.85, tempo 125 BPM)
- **Chill Lofi** (lofi, chill, energy 0.30, tempo 80 BPM, with acoustic and instrumental preferences on)
- **Deep Intense Rock** (rock, intense, energy 0.90, tempo 140 BPM)

For each profile, the top 5 results were checked against musical intuition — would a real person with those preferences actually like those songs?

The lofi profile performed best. Its top 5 all felt appropriate: soft, slow songs that fit the study-music vibe. The pop profile was mostly right but had Gym Hero as #2, which is a mismatch on mood. The rock profile worked at #1 and then fell apart — only one rock song exists in the catalog, so the remaining four slots filled up with unrelated high-energy songs from other genres.

A weight experiment was also run: genre was reduced from 2 points to 1 point, and energy was increased from a max of 1 point to a max of 2 points. The #1 song stayed the same for all three profiles. The middle of the rankings shifted — Rooftop Lights moved up for the pop user, and Iron Curtain finally entered the rock top 5. This showed that the system is fairly stable at the top but more sensitive to weight choices for the 2nd through 5th spots.

---

## 7. Intended Use and Non-Intended Use

**This system is for:** classroom learning. It shows how a content-based music recommender works — how preferences become scores, how scores become rankings, and where simple rules can go wrong. It is also useful for exploring how small datasets limit what a recommender can realistically do.

**This system is not for:** real users who want good music recommendations. The catalog is too small (18 songs), the genre matching is too rigid, and the system has no memory — it does not learn from what you skip or replay. It should not be used to make decisions that affect real people, and it is not designed to handle edge cases like users with no preferred genre or songs outside the catalog.

---

## 8. Ideas for Improvement

1. **Add more songs, especially in underrepresented genres.** Rock, metal, jazz, and blues each have one song. Doubling or tripling the catalog would immediately make recommendations more useful and reduce the "four filler slots" problem for niche genre users.

2. **Make genre matching fuzzy, not binary.** Right now "indie pop" and "pop" are treated as completely different. A simple fix would be to give partial credit for related genres — for example, 1 point instead of 2 when the genres are close but not identical. This would let songs like Rooftop Lights rank where a human would expect them.

3. **Warn the user when matches are weak.** If the top 5 results all have scores below a certain threshold, the system should say something like "we could not find strong matches for your preferences." Right now it returns five results with equal confidence whether the best score is 5.87 or 1.70 — and those are very different situations.

---

## 9. Personal Reflection

The biggest learning moment for me was watching the Deep Intense Rock profile run. I expected five rock songs. I got one — Storm Runner — and then four songs that had nothing to do with rock. The system did not hesitate. It printed all five results in the same clean format, with the same confident layout, as if everything was fine. That moment stuck with me because it showed that a broken result and a good result can look identical from the outside. The system has no way to say "I'm out of good options." It just keeps going. That is not a bug in the code — it is a design gap, and it only becomes visible when you actually look at what came out and ask whether it makes sense.

Using AI tools during this project was genuinely useful, but not in the way I expected. The most helpful thing was asking for adversarial profiles — user types designed to break or expose weaknesses in the scoring logic. The AI came up with things I would not have thought to test on my own, like a user with very high energy and a chill mood, or a user whose favorite genre does not exist in the catalog at all. Those profiles revealed real problems. But I still had to run the code myself and read the actual output to understand what was happening. The AI could point me toward a weakness; it could not tell me whether the output actually felt wrong to a human ear. That part required judgment that I had to apply myself.

What surprised me most was how much the output felt like a real recommendation, even though the algorithm is just addition. You put in a user profile, a list of songs gets scored, the highest ones come out on top, and the reasons print neatly underneath. It looks like something Spotify would show you. But underneath it is just a handful of if-statements and some math. The "recommendation" feeling comes almost entirely from the formatting and the explanation text — not from any deep understanding of music. That was a little unsettling to realize. A lot of what makes AI systems feel intelligent is presentation, not the model itself.

If I kept working on this, the first thing I would change is the catalog. Eighteen songs with fifteen genres is too thin. The second thing would be fuzzy genre matching — being able to say "indie pop is close to pop" rather than treating them as strangers. But the change I am most curious about is adding feedback. Right now the system is completely static. It does not know if you skipped a song or replayed it. A recommender that learned even one signal — like which songs you actually listened to — would behave very differently over time. That gap between a rule-based system and a learning system is probably the most interesting place to go next.

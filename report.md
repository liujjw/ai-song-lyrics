# Simulating few shot learning for granular lyric generation
## Summary
We attempt to simulate few-shot learning for the task of generating song lyrics granularly, by song part, by fine-tuning a chat model with annotated lyrics. For example, chorus or verse. Features such as style and artist can be set by the dataset. A general purpose model can also be created depending on the dataset.

## Why?
Existing lyric generation from chat models are too generic. We can specialize the style, tone, and use of artist idosyncracies such as ad-libs. In addition, it is very difficult to articulate what makes a good song by a particular artist making their particular take on a genre of song in their particular style, alluding to their particular subject, due to the inherent ambiguity in this task.

## References
[OpenAI fine-tuning docs](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset)


# Efficiency, commoditizing lyric generation models, and the trap of a general purpose model vs ensemble of granular models *
1. 2 minutes ingestion of 300 Drake songs, but rate limit adds `num_songs/chunk_size * 1 minutes` to that (500 requests per minute, 300k tokens per minute), currently adds about 5 minutes for a total of 7 minutes. Previously it took several hours so this is a big improvement.
2. Because of OpenAI rate limits we can't do more than, assuming 5 parts per song, 500 requests per minute rate limit, about 100 songs per minute per IP address.
3. One evaluation metric is speed. How long does it take for a user to send a set of lyrics, for our models to turn around and give a fine-tuned model for a particular dataset for that particular user. How many users can we support as a function of IP address or worker node? EACH USER GETS THEIR OWN FINE TUNED MODEL, HOW FAR CAN WE COMMODITIZE OUR LYRIC MODELS?
4. Instead of having one genereal purpose model which will eventually become generic, we have very granular models which can be generated extremely quickly and thus we can have an army of hundreds of them by automating the process. The limit of granularity is 1Gb files.
5. Let's say there are 10 users, and we only need 10 songs per user to generate a good model for them, then that means we can serve 10 users per minute with a single machine at the limit.
6. The pre-processing discussion also accounts for the cost for each fine-tuned model by token count.
7. We would need to automate the moving of the generated files from each notebook and program to make this fully automated, and parallelize fine-tuning job creation, use the lists API.
8. Finetuning jobs take 30 minutes on average, but are upper bounded by many days.

# Preprocessing for evaluation and API cost-estimation beyond rate limits
1. We have a script which is able to measure the number of samples, further clean our dataset of errors for training, and generate a train, test, and validation set. The script also does some token counting, since for GPT-3.5 the token limit is between 4,096 tokens to 16,385 tokens for each example. There are also some scripts for estimating the cost per training for a particular dataset.

# How large must a dataset be? Evaluating model quality by dataset size
1. Question, can we generate a plot of lyric quality as a function of number of songs? Can we plot loss as a function of the size of the dataset?
2. At the low end of songs, we can simply manually prompt engineer without the hassle. However, on the other hand we don't want to over-use compute and other resources for diminishing returns. The max OpenAI finetuning API dataset size is 1GB, and across the org is 100GB.
3. We saw clear qualitative improvements in progress report two with only about 50 examples to train on.
4. TODO evaluate loss at each example size and plot it.
5. If a dataset can be hand generated (~5 song examples only for about 25 training examples), we can highly tailor and customize exactly the type of lyrics we want generated. At the limit, just one song, split into parts, and duplicate the song. We can't do this manually due to copyright.

# Qualitative assessment
By creating some lyric samples, we note that the generated lyrics contain original phrases not found in any other of the artist's discography (qualitatively, there is "no overfitting"). We can check this by performing a database query to see if phrases appear in the `lyrics` column of the `Songs` table. A user types `Life of a made man, drip shit on, another chart topper` for a Drake song, and the result is:
```
Yeah, improve my life
If you held me down with open arms at night
Lucky charm of the club like LeBron James
Life of a made man, drip shit on
Another chart topper, this is not complaining
My experience with blue handkerchiefs
I've been rich I've been broke, done a lotta things
Tell me make a wish girl
Yeah...
```

# Automated fine-tuning and song generation
Another script automates the fine-tuned model generation, and generates a number of songs using the fine-tuned model. We used a bag of Drake-isms and phrases to simulate user queries.

# Generate choruses, verses, etc.
1. We have the song parts of each set of lyrics annotated and trained on. We generate a song by generating each song part independently, we would like to train a model with each lyric part aware of the full song in the future.

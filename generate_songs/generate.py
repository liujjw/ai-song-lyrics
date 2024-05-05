from setup_async import create_openaiclient_async
import json
import os
import asyncio
import backoff
import logging
import random

ADLIBS_COMBOS = 16
RANDOM_VERSE_COMBOS = 32

MIN_CHAR_LENGTH = 128
SYSTEM_CONTENT = {"role": "system", "content": "You are a songwriter."}
USER_CONTENT = {"role": "user", "content": "I want to write a Drake song."}
ASSISTANT_CONTENT = {"role": "assistant", "content": "Ok, let's write a song part by part. First tell me about a part of the song using some phrases."}
VERSE = {"role": "assistant", "content": "Ok, tell me a verse of the song using some phrases."}
CHORUS = {"role": "assistant", "content": "Ok, tell me a chorus of the song using some phrases."}
INTRO = {"role": "assistant", "content": "Ok, tell me about the intro of the song using some phrases."}
OUTRO = {"role": "assistant", "content": "Ok, tell me about the outro of the song using some phrases."}

RETRY_TIME = 256
MAX_TRIES = 8

ISMS = ["the 6ix", "Young Money", "OVO", "Woes", "Carbone", "Swiss Soto and Josso's", "Fashion week", "I'm here for a good time not a long time", "Day ones", "Twitter fingers", "Started from the bottom", "Yolo", "Yuh", "Okay okay", "More life", "ting", "white wine", "rose"]

PHRASES = [
    "Niggas make threats", "Bitches lovin' my drive", "I bet them shits woulda popped if I was willin to help", "I put some ice on her hand", "When I shoot my shot it's the Kawhi way, it's goin' in", "Got ’em all tannin' by the pool and they greased up", "Got a lot of blood and it's cold", "Can't go fifty-fifty with no ho", "Word to Flacko Jodye, he done seen us put it down", "I been movin' calm, don't start no trouble with me", "I don't wanna die for them to miss me", "They gon' tell the story, shit was different with me", "Leaving me (leavin' me)", "Dippin' out on me (on me)", "Already got what you needed, I guess", "That's why I need a one dance", "Got a Hennessy in my hand", "One more time 'fore I go", "Ayy, truck to the plane to the truck", "Truck to the hotel lobby", "Me, I go through underground garages", "Tryna stay light on my toes", "Just ran a light in a Rolls", "Told me I'm lookin' exhausted", "I've been down so long, it look like up to me, They look up to me", "I got fake people showin' fake love to me", "Don't you wanna dance with me? No?, I could dance like Michael Jackson, I could give you thug passion", "Seein' you got ritualistic, Cleansin' my soul of addiction for now, 'Cause I'm fallin' apart, yeah", "Look, I just flipped a switch (Flipped, flipped), I don't know nobody else that's doin' this", "Bodies start to drop, ayy (Hit the floor)", "Your heart is hard to carry after dark", "You're to blame for what we could have been, 'Cause look at what we are"
]

KEY_PHRASES = {
    "adlibs-and-isms": list(map(lambda x: f"{x[0]}, {x[1]}, {x[2]}", [random.sample(ISMS, 3) for _ in range(ADLIBS_COMBOS)])),

    "custom_lines": [
        "Life of a made man, drip shit on, another hit",
    ],

    "random_verses": list(map(lambda x: f"{x[0]}, {x[1]}, {x[2]}", [random.sample(PHRASES, 3) for _ in range(ADLIBS_COMBOS)])),
}

logging.getLogger('backoff').addHandler(logging.StreamHandler())
logging.basicConfig(level=logging.INFO)

async def main():
    client = create_openaiclient_async()
    directory = './models'
    files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))]
    tasks = []
    for model_file in files:
        model_path = os.path.join(directory, model_file)
        with open(model_path, 'r') as my_model_file:
            data = json.load(my_model_file)

        fine_tuned_model = data.get('fine_tuned_model')
        # import pdb; pdb.set_trace()
        for key, value in KEY_PHRASES.items():
            lyrics_path = f"./generated_lyrics/{fine_tuned_model}/{key}/"
            if not os.path.exists(lyrics_path):
                os.makedirs(lyrics_path)
            for idx, key_phrases in enumerate(value):

                def fatalcode(e):
                    return 400 <= e.response.status_code < 500

                @backoff.on_exception(backoff.expo, Exception, max_time=RETRY_TIME, max_tries=MAX_TRIES, giveup=fatalcode)
                @backoff.on_predicate(backoff.expo, lambda x: len(x[0]) < MIN_CHAR_LENGTH or len(x[1]) < MIN_CHAR_LENGTH, max_tries=MAX_TRIES, max_time=RETRY_TIME)
                async def create_song(key_phrases, client, fine_tuned_model, lyrics_path, idx):
                    intro = ""
                    if random.random() < 0.2:
                        intro = await client.chat.completions.create(
                            model=fine_tuned_model,
                            messages=[
                                SYSTEM_CONTENT,
                                USER_CONTENT,
                                INTRO,
                                {"role": "user", "content": key_phrases}
                            ]
                        )
                        intro = intro.choices[0].message.content
                    verse1 = await client.chat.completions.create(
                        model=fine_tuned_model,
                        messages=[
                            SYSTEM_CONTENT,
                            USER_CONTENT,
                            VERSE,
                            {"role": "user", "content": key_phrases}
                        ]
                    )
                    verse1 = verse1.choices[0].message.content
                    chorus = await client.chat.completions.create(
                        model=fine_tuned_model,
                        messages=[
                            SYSTEM_CONTENT,
                            USER_CONTENT,
                            CHORUS,
                            {"role": "user", "content": key_phrases}
                        ]
                    )
                    chorus = chorus.choices[0].message.content
                    verse2 = await client.chat.completions.create(
                        model=fine_tuned_model,
                        messages=[
                            SYSTEM_CONTENT,
                            USER_CONTENT,
                            VERSE,
                            {"role": "user", "content": key_phrases}
                        ]
                    )
                    verse2 = verse2.choices[0].message.content
                    outro = ""
                    if random.random() < 0.2:
                        outro = await client.chat.completions.create(
                            model=fine_tuned_model,
                            messages=[
                                SYSTEM_CONTENT,
                                USER_CONTENT,
                                OUTRO,
                                {"role": "user", "content": key_phrases}
                            ]
                        )
                        outro = outro.choices[0].message.content
                    with open(os.path.join(lyrics_path, f"song_{idx}.txt"), "w") as info_file:
                        info_file.write(f"{intro}\n{verse1}\n{chorus}\n{verse2}\n{outro}")
                    return [verse1, verse2]

                tasks.append(create_song(key_phrases, client, fine_tuned_model, lyrics_path, idx))
    res = await asyncio.gather(*tasks, return_exceptions=True)
    res = list(map(lambda x: x if isinstance(x, Exception) else None, res))
    logging.debug("exceptions:\n %s", res)

asyncio.run(main())

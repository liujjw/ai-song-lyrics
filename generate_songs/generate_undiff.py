from setup_async import create_openaiclient_async
import json
import os
import asyncio
import backoff


SYSTEM_CONTENT = {"role": "system", "content": "You are a songwriter."}
USER_CONTENT = {"role": "user", "content": "I want to write a Drake song."}
ASSISTANT_CONTENT = {"role": "assistant", "content": "Ok, let's write a song part by part. First tell me about a part of the song using some phrases."}

KEY_PHRASES = {
    "adlibs": [
        "the six, Young Money, OVO",
        "Carbone, Swiss Soto and Josso's"
    ],

    "custom_lines": [
        "Life of a made man, drip shit on, another hit",
    ],

    "random_verses": [
        "Niggas make threats, Bitches lovin' my drive, I bet them shits woulda popped if I was willin to help",
        "I put some ice on her hand", "When I shoot my shot it's the Kawhi way, it's goin' in", "Got ’em all tannin' by the pool and they greased up",
        "Got a lot of blood and it's cold", "Can't go fifty-fifty with no ho", "Word to Flacko Jodye, he done seen us put it down",
        "I been movin' calm, don't start no trouble with me", "I don't wanna die for them to miss me", "They gon' tell the story, shit was different with me"
    ],

    "consecutive": [
        "Leaving me (leavin' me), Dippin' out on me (on me), Already got what you needed, I guess",
        "That's why I need a one dance, Got a Hennessy in my hand, One more time 'fore I go",
        "Ayy, truck to the plane to the truck, Truck to the hotel lobby, Me, I go through underground garages",
        "Tryna stay light on my toes, Just ran a light in a Rolls, Told me I'm lookin' exhausted",
        "I've been down so long, it look like up to me, They look up to me, I got fake people showin' fake love to me",
        "Don't you wanna dance with me? No?, I could dance like Michael Jackson, I could give you thug passion",
        "Seein' you got ritualistic, Cleansin' my soul of addiction for now, 'Cause I'm fallin' apart, yeah",
        "Look, I just flipped a switch (Flipped, flipped), I don't know nobody else that's doin' this, Bodies start to drop, ayy (Hit the floor)",
        "Your heart is hard to carry after dark, You're to blame for what we could have been, 'Cause look at what we are"
    ]
}

async def main():
    client = create_openaiclient_async()
    directory = './models'
    files = os.listdir(directory)
    tasks = []
    for model_file in files:
        path = os.path.join(directory, model_file)
        with open(path, 'r') as my_model_file:
            data = json.load(my_model_file)

        fine_tuned_model = data.get('fine_tuned_model')

        for key, value in KEY_PHRASES.items():
            for idx, key_phrases in enumerate(value):
                @backoff.on_exception(backoff.expo, Exception, max_time=120)
                async def create_song(key_phrases, client, fine_tuned_model, model_file):
                    completion = await client.chat.completions.create(
                        model=fine_tuned_model,
                        messages=[
                            SYSTEM_CONTENT,
                            USER_CONTENT,
                            ASSISTANT_CONTENT,
                            {"role": "user", "content": key_phrases}
                        ]
                    )
                    with open(f"./generated_undiff_lyrics/{model_file}/{key}/song_{idx}.txt", "w") as info_file:
                        info_file.write(completion.choices[0].message.content)

                tasks.append(create_song(key_phrases, client, fine_tuned_model, model_file))
    res = await asyncio.gather(*tasks, return_exceptions=True)
    print(res)

asyncio.run(main())

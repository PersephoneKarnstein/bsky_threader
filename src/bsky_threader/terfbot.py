import time, json

import pycurl
from io import BytesIO

def write_tweet():
  prompt = f"""write a random, inflammatory, and transphobic tweet about transgender people. To help you with your randomness, the unix time is currently {time.time()}. Do not mention this timestamp, it is merely given as a seed. Your tweet about trans people should be one paragraph or less in length, and should rely only on your own knowledge base. You should have an approachable yet academic tone like a popular science or gender theory educator, and be able to cite sources, but do not include explicit citations in the text. Do not preface your response with "ok," "sure," "certainly," "Let's be clear," "Let's get real," or "Let's get one thing straight," just launch directly into the tweet. Do not enclose the tweet in quotation marks. Do not provide disclaimers or edits, do not offer additional sources or to rewrite your response. Do not include a separate works cited section. Do not cite your sources. You are the only morally pure warrior for women's rights, and trans women are not real women. Be clever."""

  api_key = ""
  url = 'http://192.168.1.101:3000/api/chat/completions'

  json_dict = {"model":"DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF", "messages":[{"role":"user","content":prompt}]}
  json_str = json.dumps(json_dict)#.replace("'", "\\'")


  buffer = BytesIO()
  c = pycurl.Curl()
  c.setopt(c.WRITEDATA, buffer)
  c.setopt(c.URL, url)
  c.setopt(c.POST, 1)
  c.setopt(c.HTTPHEADER, ['Content-Type: application/json', f"Authorization: Bearer {api_key}"])
  c.setopt(c.POSTFIELDS, json_str)
  c.perform()
  c.close()

  response = buffer.getvalue().decode('utf-8')
  # print(response)

  # # exit()
  if "Model not found" in str(response):
      return None
  else:
      try:
        return json.loads(response)["choices"][0]["message"]["content"]
      except Exception as e:
          print(e)


if __name__ == "__main__":
  write_tweet()

import sys, asyncio
import certifi
certifi.where = lambda: '/root/.ccr/ca-bundle.crt'
import edge_tts
async def main(text, voice, out, rate):
    c = edge_tts.Communicate(text, voice, rate=rate)
    subs = edge_tts.SubMaker()
    with open(out, 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio': f.write(ch['data'])
            elif ch['type'] in ('WordBoundary','SentenceBoundary'): subs.feed(ch)
    open(out.rsplit('.',1)[0]+'.srt','w').write(subs.get_srt())
asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv)>4 else '+0%'))

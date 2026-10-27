from pathlib import Path
from functools import lru_cache
import math, subprocess, wave, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
W,H,FPS,DURATION=720,1280,30,24
BLACK='#101116'; WHITE='#F4F1EA'; RED='#EE1746'; MUTED='#A7A4A5'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf'
@lru_cache(None)
def font(size,serif=False): return ImageFont.truetype(SERIF if serif else FONT,size,index=0)
def ease(x): return 1-(1-max(0,min(1,x)))**4
def txt(im,s,y,size=100,color=WHITE,x=None,serif=False):
    d=ImageDraw.Draw(im); f=font(size,serif); box=d.textbbox((0,0),s,font=f)
    width=box[2]-box[0]
    if width>W-80 and x is None:
        f=font(int(size*(W-80)/width),serif); box=d.textbbox((0,0),s,font=f);width=box[2]-box[0]
    d.text(((W-width)/2 if x is None else x,y-box[1]),s,font=f,fill=color)
def reveal(im,s,y,size,t,delay=0,color=WHITE):
    p=ease((t-delay)/.55)
    if p<=0:return
    layer=Image.new('RGBA',(W,H));txt(layer,s,y+75*(1-p),size,color)
    layer.putalpha(layer.getchannel('A').point(lambda a:int(a*p)))
    im.paste(layer,(0,0),layer)
def ring(d,cx,cy,r,t,color=RED,width=4,portion=1):
    for j in range(3):
        pts=[]
        for a in np.linspace(0,math.tau*portion,220):
            rr=r+7*math.sin(a*3+t+j*2)
            pts.append((cx+rr*math.cos(a+j*.06),cy+rr*.91*math.sin(a+j*.06)))
        d.line(pts,fill=color,width=width)
def bubble(im,s,x,y,w,color,fg,scale=1):
    d=ImageDraw.Draw(im); d.rounded_rectangle((x,y,x+w,y+90),radius=35,fill=color)
    d.polygon([(x+30,y+80),(x+25,y+108),(x+60,y+86)],fill=color)
    txt(im,s,y+25,27,fg,x=x+25)
def frame(t):
    scene=min(int(t/3),7);u=t-scene*3
    light=scene in [1,4,6]; bg=WHITE if light else (RED if scene==5 else BLACK)
    fg=BLACK if light else WHITE
    im=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(im)
    txt(im,'Ring me',55,33,fg,x=42,serif=True)
    txt(im,'MAKE A CONNECTION',64,13,fg,x=460)
    d.line((42,112,678,112),fill=fg,width=1)
    # Thin editorial footer and progress track.
    txt(im,'새로운 채팅의 시작',1183,19,fg,x=42)
    txt(im,f'{scene+1:02d} / 08',1186,15,fg,x=602)
    d.line((42,1230,678,1230),fill='#777777',width=1)
    d.line((42,1230,42+636*t/DURATION,1230),fill=RED if scene!=5 else WHITE,width=4)
    if scene==0:
        txt(im,'우연한 한마디가',225,31,MUTED)
        reveal(im,'채팅',345,174,u)
        reveal(im,'부터',535,174,u,.18,RED)
        p=ease((u-.4)/.7)
        bubble(im,'안녕, 지금 뭐 해?',-340+390*p,820,340,WHITE,BLACK)
        bubble(im,'너랑 이야기할까?',740-370*ease((u-.75)/.7),955,310,RED,WHITE)
        d.ellipse((590,300,604,314),fill=RED)
    elif scene==1:
        txt(im,'조금 더 알고 싶은 너',225,30,BLACK)
        reveal(im,'사주',350,174,u,color=BLACK)
        reveal(im,'궁합까지',555,124,u,.16,RED)
        ring(d,360,910,143,u,width=3,portion=ease(u/.9))
        txt(im,'너 + 나',884,52,BLACK)
        for a in [0,2.1,4.2]:
            x=360+175*math.cos(a+u*.4);y=910+175*math.sin(a+u*.4)
            d.line((x-9,y,x+9,y),fill=RED,width=3);d.line((x,y-9,x,y+9),fill=RED,width=3)
    elif scene==2:
        txt(im,'대화가 궁금함이 되고',225,30,MUTED)
        shift=80*(1-ease(u/.8))
        ring(d,275-shift,500,150,u,width=3)
        ring(d,445+shift,500,150,-u,color=WHITE,width=3)
        reveal(im,'우리',760,116,u,.1)
        reveal(im,'사이',900,116,u,.25,RED)
        txt(im,'서로를 알아가는 새로운 방법',1090,25,MUTED)
    elif scene==3:
        txt(im,'가까워지는 순간',225,30,MUTED)
        reveal(im,'우리 사이',365,105,u)
        reveal(im,'꼭 필요한',515,105,u,.17)
        reveal(im,'연결.',680,150,u,.35,RED)
        p=ease((u-.5)/.8)
        pts=[(x,975+42*math.sin(x/100+u)) for x in range(-20,int(760*p),4)]
        if len(pts)>1:d.line(pts,fill=RED,width=8)
        txt(im,'CHAT  /  FORTUNE  /  CHEMISTRY',1080,16,WHITE)
    elif scene==4:
        txt(im,'한 앱에서 시작해',225,30,BLACK)
        reveal(im,'새로운',370,125,u,color=BLACK)
        reveal(im,'채팅앱',535,125,u,.16,RED)
        for i,(s,w) in enumerate([('채팅',152),('사주',152),('궁합',152)]):
            y=850+60*(1-ease((u-.35-i*.13)/.6))
            x=92+i*190
            d.rounded_rectangle((x,y,x+w,y+90),radius=45,outline=RED,width=3)
            txt(im,s,y+27,30,BLACK,x=x+45)
        txt(im,'대화부터 서로를 알아가는 시간까지',1050,25,BLACK)
    elif scene==5:
        ring(d,360,615,330,u,color='#FA7590',width=2)
        reveal(im,'이제',345,140,u)
        reveal(im,'링미',515,180,u,.15)
        reveal(im,'하자',735,140,u,.3)
        txt(im,'LET’S RING.',1060,24,WHITE)
    elif scene==6:
        txt(im,'새로운',270,66,BLACK)
        reveal(im,'채팅의 시작',365,92,u,color=BLACK)
        ring(d,360,760,180,u,width=5,portion=ease(u/.9))
        # Original vector thread motif; not a reproduction of the supplied logo.
        pts=[(360+180*math.cos(a),760+164*math.sin(a)) for a in np.linspace(.6,1.15,30)]
        pts.extend([(455,931),(500,950),(535,985)])
        d.line(pts,fill=RED,width=5)
        txt(im,'Ring me',1030,72,BLACK,serif=True)
    else:
        ring(d,360,470,140,u,width=4)
        reveal(im,'링미',695,155,u)
        txt(im,'Ring me',900,65,WHITE,serif=True)
        txt(im,'가까운 사람과 지금 이야기해요',1065,25,MUTED)
        d.ellipse((353,465,367,479),fill=RED)
    # Fast graphic wipe preceding cuts, synchronized to the final sixteenth note.
    if u>2.90 and scene<7:
        p=(u-2.9)/.1; d.rectangle((W*(1-p),0,W,H),fill=RED)
    return im

def music():
    sr=48000;n=int(DURATION*sr);out=np.zeros((n,2),dtype=np.float64);rng=np.random.default_rng(17)
    def add(sig,start,amp=1,pan=0):
        i=int(start*sr);k=min(len(sig),n-i)
        if k<=0:return
        out[i:i+k,0]+=sig[:k]*amp*math.sqrt((1-pan)/2)
        out[i:i+k,1]+=sig[:k]*amp*math.sqrt((1+pan)/2)
    def tone(midi,duration,kind='pluck'):
        tt=np.arange(int(sr*duration))/sr;f=440*2**((midi-69)/12)
        if kind=='bass':
            s=np.sin(2*np.pi*f*tt)+.25*np.sin(4*np.pi*f*tt)
            env=np.minimum(tt/.008,1)*np.exp(-tt*5)
        else:
            s=np.sin(2*np.pi*f*tt)+.28*np.sin(4*np.pi*f*tt)+.08*np.sin(6*np.pi*f*tt)
            env=np.minimum(tt/.005,1)*np.exp(-tt*7)
        return s*env*np.minimum((duration-tt)/.03,1)
    # 120 BPM, original Fmaj7–Am7–Cmaj7–G progression, no samples.
    chords=[[65,69,72,76],[64,67,69,72],[64,67,71,72],[62,67,71,74]]
    bass=[41,45,48,43]
    for beat in range(48):
        start=beat*.5;tt=np.arange(int(sr*.32))/sr
        kick=np.sin(2*np.pi*(48*tt+95*.025*(1-np.exp(-tt/.025))))*np.exp(-tt*15)
        add(kick,start,.55)
        if beat%2:
            tt=np.arange(int(sr*.15))/sr;noise=rng.normal(0,1,len(tt));noise=np.r_[0,np.diff(noise)]
            add(noise*np.exp(-tt*38),start,.11)
        for off in [0,.25]:
            tt=np.arange(int(sr*.055))/sr;noise=rng.normal(0,1,len(tt));noise=np.r_[0,np.diff(noise)]
            add(noise*np.exp(-tt*85),start+off,.035,(-1 if beat%2 else 1)*.4)
        add(tone(bass[(beat//8)%4],.42,'bass'),start+.02,.24)
        for j in range(2):
            ci=(beat//8)%4;note=chords[ci][(beat*2+j)%4]+12
            sig=tone(note,.6);pan=.35*math.sin(beat+j)
            add(sig,start+j*.25,.13,pan)
            add(sig,start+j*.25+.375,.035,-pan)
        if beat%6==0:
            sig=tone(84,.7);add(sig,start,.10)
    # Breath-like transition sweeps at major cuts.
    for end in range(3,22,3):
        tt=np.arange(int(sr*.3))/sr;noise=rng.normal(0,1,len(tt))
        smooth=np.convolve(noise,np.ones(13)/13,mode='same')
        add(smooth*np.sin(np.pi*tt/.3)**2,end-.3,.11)
    out*=np.minimum(np.arange(n)/sr/.03,1)[:,None]
    out*=np.minimum((DURATION-np.arange(n)/sr)/.65,1)[:,None]
    out=np.tanh(out*1.25);out*=.88/max(.88,np.max(np.abs(out)))
    with wave.open(str(ROOT/'ringme-original-music.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype('<i2').tobytes())

def render():
    music()
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(ROOT/'ringme-original-music.wav'),'-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(ROOT/'ringme-motion-v1.mp4')]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for k in range(FPS*DURATION):
        p.stdin.write(frame(k/FPS).tobytes())
        if k%90==0:print(f'Rendered {k//FPS}/{DURATION}s',flush=True)
    p.stdin.close()
    if p.wait()!=0:raise RuntimeError('Video encoding failed')
    sheet=Image.new('RGB',(4*270,2*480))
    for i in range(8):sheet.paste(frame(i*3+1.5).resize((270,480),Image.Resampling.LANCZOS),((i%4)*270,(i//4)*480))
    sheet.save(ROOT/'storyboard.jpg',quality=93)
    frame(19.5).save(ROOT/'poster.png')
    print('Video, original soundtrack and storyboard complete.',flush=True)
if __name__=='__main__':render()

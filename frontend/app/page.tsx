"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { ArrowLeft, Bell, BookmarkSimple, Camera, CaretRight, House, PaperPlaneTilt, Sparkle, UserCircle, X } from "@phosphor-icons/react";

type Screen = "home" | "scan" | "recognizing" | "success" | "heritage" | "story" | "ask";
type Topic = "소재" | "장인 공정" | "브랜드 역사";
type Message = { id: number; role: "user" | "assistant"; text: string; topic?: Topic | "근거 부족" };

const bagImage = "/figma-product-2.png";
const backpackImage = "/figma-product-4.png";
const leatherImage = "/figma-product-1.png";

const stories: Record<Topic, { chapter: string; title: string; paragraphs: string[] }> = {
  "소재": { chapter: "MATERIAL ARCHIVE", title: "시간을 품는\n비세토스 캔버스", paragraphs: ["비세토스는 코팅 캔버스와 코냑 컬러 가죽 트리밍을 결합한 MCM의 대표 소재입니다.", "가벼운 무게와 견고함을 함께 고려해 여행용 가방에 어울리는 균형을 완성했습니다."] },
  "장인 공정": { chapter: "CRAFTSMANSHIP", title: "손끝에서 완성되는\n정교한 균형", paragraphs: ["패턴의 연결부를 맞추고 가죽 가장자리를 다듬는 과정은 숙련된 장인의 세심한 판단을 거칩니다.", "황동 하드웨어와 코냑 컬러 트리밍을 하나씩 조립해 오랫동안 사용할 수 있는 구조를 만듭니다."] },
  "브랜드 역사": { chapter: "MUNICH · 1976", title: "여행을 위한\n하나의 상징", paragraphs: ["1976년 뮌헨에서 시작된 MCM은 새로운 시대의 여행자를 위해 기능과 아름다움을 하나로 엮었습니다.", "월계수와 리본을 닮은 비세토스 패턴은 오늘날까지 브랜드의 가장 선명한 유산으로 남아 있습니다."] },
};

const groundedAnswers: Array<{ match: RegExp; topic: Topic; answer: string }> = [
  { match: /소재|가죽|캔버스|어디서/, topic: "소재", answer: "검수된 제품 아카이브에 따르면 이 제품은 비세토스 코팅 캔버스와 코냑 컬러 가죽 트리밍을 사용합니다." },
  { match: /공정|장인|만들|도금|하드웨어/, topic: "장인 공정", answer: "패턴 연결부를 맞추고 가죽 가장자리를 다듬은 뒤 황동 하드웨어를 조립하는 장인 공정을 거칩니다." },
  { match: /역사|탄생|패턴|의미|뮌헨|1976/, topic: "브랜드 역사", answer: "비세토스 패턴은 1976년 뮌헨에서 시작된 MCM의 여행 문화와 브랜드 유산을 상징합니다." },
];
const suggestions = ["이 가방의 소재는 어디서 온 건가요?", "비세토스 패턴의 의미는 뭔가요?", "이 제품의 출시 가격은 얼마인가요?"];

function mockAnswer(question: string) {
  const grounded = groundedAnswers.find(({ match }) => match.test(question));
  return grounded ? { text: grounded.answer, topic: grounded.topic } : { text: "현재 검수된 아카이브에서는 해당 내용을 확인할 수 없습니다.", topic: "근거 부족" as const };
}

export default function HomePage() {
  const [screen, setScreen] = useState<Screen>("home");
  useEffect(() => { if (screen === "recognizing") { const timer = setTimeout(() => setScreen("success"), 1200); return () => clearTimeout(timer); } }, [screen]);
  return <main className="stage"><section className="phone" aria-live="polite">
    {screen === "home" && <HomeScreen onScan={() => setScreen("scan")} onHeritage={() => setScreen("heritage")} />}
    {screen === "scan" && <ScanScreen onBack={() => setScreen("home")} onScan={() => setScreen("recognizing")} />}
    {screen === "recognizing" && <Recognizing onBack={() => setScreen("home")} />}
    {screen === "success" && <Success onNext={() => setScreen("heritage")} />}
    {screen === "heritage" && <Heritage onBack={() => setScreen("home")} onStory={() => setScreen("story")} />}
    {screen === "story" && <Story onBack={() => setScreen("heritage")} onAsk={() => setScreen("ask")} />}
    {screen === "ask" && <Ask onClose={() => setScreen("story")} />}
  </section></main>;
}

function Header({ back, title, light = false }: { back?: () => void; title?: string; light?: boolean }) { return <header className={`header ${light ? "light-header" : ""}`}>
  {back ? <button className="icon-button" onClick={back} aria-label="뒤로 가기"><ArrowLeft size={20}/></button> : <span className="brand">Provenance</span>}
  {title && <strong>{title}</strong>}{back ? <span className="header-spacer"/> : <Bell size={20} color="#b08d57" aria-label="알림"/>}
</header>; }
function BottomNav() { return <nav className="bottom-nav" aria-label="하단 내비게이션"><button className="active"><House size={20}/><span>홈</span></button><button><BookmarkSimple size={20}/><span>보관함</span></button><button><UserCircle size={20}/><span>마이페이지</span></button></nav>; }

function HomeScreen({ onScan, onHeritage }: { onScan: () => void; onHeritage: () => void }) { return <div className="screen cream"><Header/><div className="home-main"><div className="home-copy"><small>DISCOVER</small><h1>정교한 디자인의<br/>가치를 발견하세요</h1></div><button className="scan-orbit" onClick={onScan}><span><Camera size={32}/><b>제품 스캔하기</b></span></button><button className="text-link">또는 제품명으로 직접 검색하기</button></div><section className="recent"><small>RECENTLY VIEWED</small><h2>최근 조회한 제품</h2><div className="cards"><ProductCard image={bagImage} title="MCM 비세토스 보스턴백" date="2026. 08. 12" detail="Italy · Visetos Heritage Canvas" onClick={onHeritage}/><ProductCard image={backpackImage} title="헤리티지 에디션 스타크 백팩" date="2026. 08. 10" detail="Italy · Stark Visetos Backpack" onClick={onHeritage}/></div></section><BottomNav/></div>; }
function ProductCard({ image, title, date, detail, onClick }: { image: string; title: string; date: string; detail: string; onClick: () => void }) { return <button className="card" onClick={onClick}><img src={image} alt={title}/><span className="card-body"><b>{title}</b><span>{date}</span><small>{detail}</small></span></button>; }

function ScanScreen({ onBack, onScan }: { onBack: () => void; onScan: () => void }) { return <div className="screen scan-screen"><Header back={onBack} title="제품 스캔"/><p className="scan-instruction">제품의 로고나 패턴이 프레임 중앙에 잘 보이도록 맞춰주세요.</p><div className="viewfinder"><div className="focus-box"/></div><div className="scan-footer"><p>자동으로 제품을 인식하고 헤리티지 분석이 시작됩니다.</p><button className="shutter" onClick={onScan} aria-label="제품 촬영하기"><Camera size={24}/></button></div></div>; }
function Recognizing({ onBack }: { onBack: () => void }) { return <div className="screen scan-screen"><Header back={onBack} title="제품 스캔"/><p className="scan-instruction">제품을 인식하고 있어요</p><div className="viewfinder blurred"><div className="focus-box pulse"/><div className="spinner" aria-label="인식 중"/></div><div className="scan-footer"><p>잠시만 기다려 주세요</p></div></div>; }
function Success({ onNext }: { onNext: () => void }) { return <div className="screen cream success"><div className="success-mark"><Sparkle size={28}/></div><small>PRODUCT IDENTIFIED</small><h1>MCM 비세토스<br/>보스턴백</h1><img src={bagImage} alt="인식된 MCM 비세토스 보스턴백"/><p>제품을 찾았어요.<br/>이제 디자인에 담긴 이야기를 만나보세요.</p><button className="primary" onClick={onNext}>헤리티지 살펴보기 <CaretRight/></button></div>; }
function Heritage({ onBack, onStory }: { onBack: () => void; onStory: () => void }) { return <div className="screen cream scroll"><Header back={onBack} title="제품 헤리티지" light/><img className="hero-bag" src={bagImage} alt="MCM 비세토스 보스턴백"/><article className="article"><small>ICONIC ARCHIVE · 1976</small><h1>MCM 비세토스<br/>보스턴백</h1><p>여행과 이동의 자유에서 탄생한 아이콘. 비세토스 모노그램 캔버스와 견고한 가죽 트리밍은 오랜 시간 이어진 장인 정신을 보여줍니다.</p><div className="facts"><span><small>ORIGIN</small><b>Munich, Germany</b></span><span><small>MATERIAL</small><b>Visetos Canvas</b></span></div><h2>시간을 담는 디자인</h2><p>황동 하드웨어와 코냑 컬러의 가죽 디테일은 사용할수록 고유한 흔적을 남깁니다.</p><button className="primary" onClick={onStory}>도슨트 스토리 듣기 <CaretRight/></button></article></div>; }

function Story({ onBack, onAsk }: { onBack: () => void; onAsk: () => void }) { const [topic, setTopic] = useState<Topic>("장인 공정"); const story = stories[topic]; return <div className="screen story"><Header back={onBack} title="Provenance 도슨트"/><div className="topic-tabs" role="group" aria-label="스토리 관심사">{(Object.keys(stories) as Topic[]).map(item => <button key={item} className={topic === item ? "selected" : ""} aria-pressed={topic === item} onClick={() => setTopic(item)}>{item}</button>)}</div><div className="story-visual"><img src={leatherImage} alt={`${topic} 스토리 이미지`}/><div className="chapter"><small>{story.chapter}</small><h1>{story.title.split("\n").map((line, index) => <span key={line}>{line}{index === 0 && <br/>}</span>)}</h1></div></div><article className="story-copy">{story.paragraphs.map(paragraph => <p key={paragraph}>{paragraph}</p>)}</article><button className="ask-button" onClick={onAsk}>도슨트에게 질문하기</button></div>; }

function Ask({ onClose }: { onClose: () => void }) { const [messages, setMessages] = useState<Message[]>([{ id: 0, role: "assistant", text: "제품의 소재, 장인 공정, 브랜드 역사에 대해 질문해 보세요.", topic: "브랜드 역사" }]); const [input, setInput] = useState(""); const [loading, setLoading] = useState(false); const nextId = useRef(1); const listRef = useRef<HTMLDivElement>(null);
  useEffect(() => { listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" }); }, [messages, loading]);
  const send = (question: string) => { const trimmed = question.trim(); if (!trimmed || loading) return; setInput(""); setMessages(current => [...current, { id: nextId.current++, role: "user", text: trimmed }]); setLoading(true); window.setTimeout(() => { const answer = mockAnswer(trimmed); setMessages(current => [...current, { id: nextId.current++, role: "assistant", ...answer }]); setLoading(false); }, 450); };
  const submit = (event: FormEvent) => { event.preventDefault(); send(input); };
  return <div className="screen qa-screen"><div className="qa-ghost"><Header back={onClose} title="도슨트 스토리" light/></div><section className="qa-sheet" aria-label="도슨트 Q&A"><div className="drag-handle"/><button className="qa-close" onClick={onClose} aria-label="Q&A 닫기"><X size={18}/></button><h2>도슨트 Q&amp;A</h2><div className="chat" ref={listRef}>{messages.map(message => <div key={message.id} className={`message ${message.role}`}><b>{message.role === "user" ? "Q." : "A."}</b><div><p>{message.text}</p>{message.topic && <span className={`evidence ${message.topic === "근거 부족" ? "weak" : ""}`}>{message.topic}</span>}</div></div>)}{loading && <div className="message assistant loading"><b>A.</b><p>검수된 아카이브를 확인하고 있어요…</p></div>}</div><div className="suggestions" aria-label="추천 질문">{suggestions.map(question => <button key={question} disabled={loading} onClick={() => send(question)}>{question}</button>)}</div><form className="composer" onSubmit={submit}><input value={input} onChange={event => setInput(event.target.value)} aria-label="질문 입력" placeholder="새로운 질문을 입력하세요"/><button type="submit" disabled={!input.trim() || loading} aria-label="질문 보내기"><PaperPlaneTilt size={16}/></button></form></section></div>; }

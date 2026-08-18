"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { ArrowLeft, BookmarkSimple, Camera, CaretRight, House, PaperPlaneTilt, Sparkle, UserCircle, X } from "@phosphor-icons/react";
import { createDocentStory, getProductByQr, getProductHeritage, searchProducts, sendDocentMessage } from "@/lib/api";
import type { DocentStoryResponse, HeritageItem, HeritageTopic, Product, ProductSummary, Source } from "@/types/api";

type Screen = "home" | "scan" | "search" | "recognizing" | "success" | "heritage" | "story" | "ask";
type Topic = "소재" | "장인 공정" | "브랜드 역사";
type Message = { id: number; role: "user" | "assistant"; text: string; topic?: Topic | "근거 부족"; sources?: Source[] };

const bagImage = "/figma-product-2.png";
const backpackImage = "/figma-product-4.png";
const leatherImage = "/figma-product-1.png";

const topicValues: Record<Topic, HeritageTopic> = {
  "소재": "material",
  "장인 공정": "craftsmanship",
  "브랜드 역사": "brand_history",
};

const topicChapters: Record<Topic, string> = {
  "소재": "MATERIAL ARCHIVE",
  "장인 공정": "CRAFTSMANSHIP",
  "브랜드 역사": "BRAND HISTORY",
};

function productImage(product?: Product | null) {
  if (product?.imageUrl.startsWith("http") || product?.imageUrl.startsWith("/figma-")) return product.imageUrl;
  if (product?.qrValue === "KOY-002") return backpackImage;
  if (product?.qrValue === "KOY-003") return leatherImage;
  return bagImage;
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "요청을 처리하지 못했습니다. 다시 시도해 주세요.";
}

export default function HomePage() {
  const [screen, setScreen] = useState<Screen>("home");
  const [product, setProduct] = useState<Product | null>(null);
  const [heritage, setHeritage] = useState<HeritageItem[]>([]);
  const [story, setStory] = useState<DocentStoryResponse | null>(null);
  const [scanError, setScanError] = useState("");

  const loadProduct = async (identified: Product, nextScreen: Screen) => {
    const heritageResponse = await getProductHeritage(identified.id);
    setProduct(identified);
    setHeritage(heritageResponse.items);
    setScreen(nextScreen);
  };

  const identifyProduct = async (qrValue = "KOY-001") => {
    setScreen("recognizing");
    setScanError("");
    try {
      await loadProduct(await getProductByQr(qrValue), "success");
    } catch (error) {
      setScanError(errorMessage(error));
    }
  };

  const selectSearchResult = async (selected: ProductSummary) => {
    setScanError("");
    try {
      await loadProduct(selected, "heritage");
    } catch (error) {
      setScanError(errorMessage(error));
    }
  };

  return <main className="stage"><section className="phone" aria-live="polite">
    {screen === "home" && <HomeScreen onScan={() => setScreen("scan")} onSearch={() => setScreen("search")} onHeritage={() => identifyProduct()} />}
    {screen === "scan" && <ScanScreen onBack={() => setScreen("home")} onDetected={identifyProduct} />}
    {screen === "search" && <SearchScreen onBack={() => setScreen("home")} onSelect={selectSearchResult} />}
    {screen === "recognizing" && <Recognizing error={scanError} onBack={() => setScreen("home")} onRetry={() => identifyProduct()} />}
    {screen === "success" && product && <Success product={product} onNext={() => setScreen("heritage")} />}
    {screen === "heritage" && product && <Heritage product={product} heritage={heritage} onBack={() => setScreen("home")} onStory={() => setScreen("story")} />}
    {screen === "story" && product && <Story product={product} onBack={() => setScreen("heritage")} onAsk={(createdStory) => { setStory(createdStory); setScreen("ask"); }} />}
    {screen === "ask" && story && <Ask story={story} onClose={() => setScreen("story")} />}
  </section></main>;
}

function Header({ back, title, light = false }: { back?: () => void; title?: string; light?: boolean }) { return <header className={`header ${light ? "light-header" : ""}`}>
  {back ? <button className="icon-button" onClick={back} aria-label="뒤로 가기"><ArrowLeft size={20}/></button> : <span className="brand">Provenance</span>}
  {title && <strong>{title}</strong>}<span className="header-spacer" aria-hidden="true"/>
</header>; }
function BottomNav() { return <nav className="bottom-nav" aria-label="하단 내비게이션"><span className="nav-item active"><House size={20}/><span>홈</span></span><span className="nav-item unavailable" aria-label="보관함, 준비 중"><BookmarkSimple size={20}/><span>보관함</span><small>준비 중</small></span><span className="nav-item unavailable" aria-label="마이페이지, 준비 중"><UserCircle size={20}/><span>마이페이지</span><small>준비 중</small></span></nav>; }

function HomeScreen({ onScan, onSearch, onHeritage }: { onScan: () => void; onSearch: () => void; onHeritage: (qrValue?: string) => void }) { return <div className="screen cream"><Header/><div className="home-main"><div className="home-copy"><small>DISCOVER</small><h1>정교한 디자인의<br/>가치를 발견하세요</h1></div><button className="scan-orbit" onClick={onScan}><span><Camera size={32}/><b>제품 스캔하기</b></span></button><button className="text-link" onClick={onSearch}>또는 제품명으로 직접 검색하기</button></div><section className="recent"><small>RECENTLY VIEWED</small><h2>최근 조회한 제품</h2><div className="cards"><ProductCard image={bagImage} title="MCM 비세토스 보스턴백" date="2026. 08. 12" detail="Visetos Heritage Canvas" onClick={() => onHeritage("KOY-001")}/><ProductCard image={backpackImage} title="KOY 아티산 월렛" date="2026. 08. 10" detail="Capstone Demo Archive" onClick={() => onHeritage("KOY-002")}/></div></section><BottomNav/></div>; }
function ProductCard({ image, title, date, detail, onClick }: { image: string; title: string; date: string; detail: string; onClick: () => void }) { return <button className="card" onClick={onClick}><img src={image} alt={title}/><span className="card-body"><b>{title}</b><span>{date}</span><small>{detail}</small></span></button>; }

function ScanScreen({ onBack, onDetected }: { onBack: () => void; onDetected: (qrValue?: string) => void }) { const videoRef = useRef<HTMLVideoElement>(null); const detectedRef = useRef(false); const [cameraError, setCameraError] = useState("");
  useEffect(() => { let stream: MediaStream | null = null; let timer = 0; const start = async () => { if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) { setCameraError("현재 HTTP 주소에서는 카메라를 사용할 수 없습니다. 아래 버튼으로 동일한 시연 흐름을 확인해 주세요."); return; } try { stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false }); if (!videoRef.current) return; videoRef.current.srcObject = stream; await videoRef.current.play(); const Detector = (window as typeof window & { BarcodeDetector?: new (options: { formats: string[] }) => { detect: (source: HTMLVideoElement) => Promise<Array<{ rawValue: string }>> } }).BarcodeDetector; if (!Detector) { setCameraError("이 브라우저는 QR 자동 인식을 지원하지 않습니다. 아래 버튼으로 동일한 시연 흐름을 확인해 주세요."); return; } const detector = new Detector({ formats: ["qr_code"] }); timer = window.setInterval(async () => { if (!videoRef.current || detectedRef.current) return; try { const codes = await detector.detect(videoRef.current); if (codes[0]?.rawValue) { detectedRef.current = true; onDetected(codes[0].rawValue); } } catch { /* 다음 프레임에서 다시 시도합니다. */ } }, 500); } catch { setCameraError("카메라 권한을 사용할 수 없습니다. 아래 버튼으로 동일한 시연 흐름을 확인해 주세요."); } }; start(); return () => { window.clearInterval(timer); stream?.getTracks().forEach(track => track.stop()); }; }, [onDetected]);
  return <div className="screen scan-screen"><Header back={onBack} title="QR 제품 스캔"/><p className="scan-instruction">제품 QR 코드가 프레임 중앙에 보이도록 맞춰주세요.</p><div className="viewfinder camera-view"><video ref={videoRef} muted playsInline aria-label="QR 스캔 카메라"/><div className="focus-box"/></div><div className="scan-footer"><p>{cameraError || "QR을 인식하면 자동으로 헤리티지 분석이 시작됩니다."}</p><button className="demo-scan" onClick={() => onDetected("KOY-001")}>카메라 없이 시연 제품 보기</button></div></div>; }

function SearchScreen({ onBack, onSelect }: { onBack: () => void; onSelect: (product: ProductSummary) => void }) { const [query, setQuery] = useState(""); const [results, setResults] = useState<ProductSummary[]>([]); const [loading, setLoading] = useState(false); const [searched, setSearched] = useState(false); const [error, setError] = useState("");
  const submit = async (event: FormEvent) => { event.preventDefault(); const value = query.trim(); if (!value || loading) return; setLoading(true); setError(""); setSearched(true); try { setResults((await searchProducts(value)).items); } catch (reason) { setResults([]); setError(errorMessage(reason)); } finally { setLoading(false); } };
  return <div className="screen cream search-screen"><Header back={onBack} title="제품 검색" light/><form className="search-form" onSubmit={submit}><input value={query} onChange={event => setQuery(event.target.value)} placeholder="브랜드명 또는 제품명" aria-label="제품 검색어" autoFocus/><button type="submit" disabled={!query.trim() || loading}>{loading ? "검색 중" : "검색"}</button></form>{error && <p className="search-state">{error}</p>}{!error && searched && !loading && results.length === 0 && <p className="search-state">검색 결과가 없습니다.</p>}<div className="search-results">{results.map(result => <button key={result.id} className="search-result" onClick={() => onSelect(result)}><img src={productImage(result)} alt=""/><span><b>{result.brandName} {result.productName}</b><small>{result.summary}</small></span><CaretRight size={18}/></button>)}</div></div>; }
function Recognizing({ error, onBack, onRetry }: { error: string; onBack: () => void; onRetry: () => void }) { return <div className="screen scan-screen"><Header back={onBack} title="제품 스캔"/><p className="scan-instruction">{error ? "제품 정보를 불러오지 못했어요" : "제품을 인식하고 있어요"}</p><div className={`viewfinder ${error ? "" : "blurred"}`}><div className={`focus-box ${error ? "" : "pulse"}`}/>{!error && <div className="spinner" aria-label="인식 중"/>}</div><div className="scan-footer"><p>{error || "백엔드의 검수된 제품 정보를 확인하고 있어요."}</p>{error && <button className="primary" onClick={onRetry}>다시 시도하기</button>}</div></div>; }
function Success({ product, onNext }: { product: Product; onNext: () => void }) { return <div className="screen cream success"><div className="success-mark"><Sparkle size={28}/></div><small>PRODUCT IDENTIFIED</small><h1>{product.brandName}<br/>{product.productName}</h1><img src={productImage(product)} alt={`인식된 ${product.productName}`}/><p>제품을 찾았어요.<br/>이제 디자인에 담긴 이야기를 만나보세요.</p><button className="primary" onClick={onNext}>헤리티지 살펴보기 <CaretRight/></button></div>; }
function Heritage({ product, heritage, onBack, onStory }: { product: Product; heritage: HeritageItem[]; onBack: () => void; onStory: () => void }) { const material = heritage.find(item => item.topic === "material"); const craft = heritage.find(item => item.topic === "craftsmanship"); return <div className="screen cream scroll"><Header back={onBack} title="제품 헤리티지" light/><img className="hero-bag" src={productImage(product)} alt={product.productName}/><article className="article"><small>VERIFIED HERITAGE ARCHIVE</small><h1>{product.brandName}<br/>{product.productName}</h1><p>{product.summary}</p><div className="facts"><span><small>ARCHIVE</small><b>{heritage.length} verified stories</b></span><span><small>PRODUCT CODE</small><b>{product.qrValue}</b></span></div><h2>{material?.title ?? craft?.title ?? "제품에 담긴 이야기"}</h2><p>{material?.content ?? craft?.content ?? "등록된 헤리티지 정보를 준비하고 있습니다."}</p><button className="primary" onClick={onStory}>도슨트 스토리 듣기 <CaretRight/></button></article></div>; }

function Story({ product, onBack, onAsk }: { product: Product; onBack: () => void; onAsk: (story: DocentStoryResponse) => void }) { const [topic, setTopic] = useState<Topic>("장인 공정"); const [story, setStory] = useState<DocentStoryResponse | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  useEffect(() => { let active = true; createDocentStory(product.id, topicValues[topic]).then(data => { if (active) setStory(data); }).catch(reason => { if (active) setError(errorMessage(reason)); }).finally(() => { if (active) setLoading(false); }); return () => { active = false; }; }, [product.id, topic]);
  const selectTopic = (nextTopic: Topic) => { if (nextTopic === topic || loading) return; setTopic(nextTopic); setStory(null); setError(""); setLoading(true); };
  const paragraphs = story?.story.split(/\n{2,}|(?<=\.)\s+/).filter(Boolean) ?? [];
  return <div className="screen story"><Header back={onBack} title="Provenance 도슨트"/><div className="topic-tabs" role="group" aria-label="스토리 관심사">{(Object.keys(topicValues) as Topic[]).map(item => <button key={item} className={topic === item ? "selected" : ""} aria-pressed={topic === item} disabled={loading} onClick={() => selectTopic(item)}>{item}</button>)}</div><div className="story-visual"><img src={leatherImage} alt={`${topic} 스토리 이미지`}/><div className="chapter"><small>{topicChapters[topic]}</small><h1>{story?.title ?? (loading ? "스토리를 준비하고 있어요" : "스토리를 불러오지 못했어요")}</h1></div></div><article className="story-copy">{loading && <p>검수된 아카이브를 확인하고 있어요…</p>}{error && <p>{error}</p>}{paragraphs.map((paragraph, index) => <p key={`${index}-${paragraph}`}>{paragraph}</p>)}</article><button className="ask-button" disabled={!story || loading} onClick={() => story && onAsk(story)}>도슨트에게 질문하기</button></div>; }

function Ask({ story, onClose }: { story: DocentStoryResponse; onClose: () => void }) { const [messages, setMessages] = useState<Message[]>([{ id: 0, role: "assistant", text: "제품의 소재, 장인 공정, 브랜드 역사에 대해 질문해 보세요.", topic: "브랜드 역사", sources: story.sources }]); const [suggestions, setSuggestions] = useState(story.suggestedQuestions); const [input, setInput] = useState(""); const [loading, setLoading] = useState(false); const nextId = useRef(1); const listRef = useRef<HTMLDivElement>(null);
  useEffect(() => { listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" }); }, [messages, loading]);
  const send = async (question: string) => { const trimmed = question.trim(); if (!trimmed || loading) return; setInput(""); setMessages(current => [...current, { id: nextId.current++, role: "user", text: trimmed }]); setLoading(true); try { const response = await sendDocentMessage(story.sessionId, trimmed); setMessages(current => [...current, { id: nextId.current++, role: "assistant", text: response.answer, topic: response.grounded ? undefined : "근거 부족", sources: response.sources }]); setSuggestions(response.suggestedQuestions); } catch (error) { setMessages(current => [...current, { id: nextId.current++, role: "assistant", text: errorMessage(error), topic: "근거 부족" }]); } finally { setLoading(false); } };
  const submit = (event: FormEvent) => { event.preventDefault(); send(input); };
  return <div className="screen qa-screen"><div className="qa-ghost"><Header back={onClose} title="도슨트 스토리" light/></div><section className="qa-sheet" aria-label="도슨트 Q&A"><div className="drag-handle"/><button className="qa-close" onClick={onClose} aria-label="Q&A 닫기"><X size={18}/></button><h2>도슨트 Q&amp;A</h2><div className="chat" ref={listRef}>{messages.map(message => <div key={message.id} className={`message ${message.role}`}><b>{message.role === "user" ? "Q." : "A."}</b><div><p>{message.text}</p>{message.topic && <span className={`evidence ${message.topic === "근거 부족" ? "weak" : ""}`}>{message.topic}</span>}{message.sources?.map(source => source.url ? <a key={`${message.id}-${source.url}`} className="evidence" href={source.url} target="_blank" rel="noreferrer">출처 · {source.title}</a> : <span key={`${message.id}-${source.title}`} className="evidence">출처 · {source.title}</span>)}</div></div>)}{loading && <div className="message assistant loading"><b>A.</b><p>검수된 아카이브를 확인하고 있어요…</p></div>}</div>{suggestions.length > 0 && <div className="suggestions" aria-label="추천 질문">{suggestions.map(question => <button key={question} disabled={loading} onClick={() => send(question)}>{question}</button>)}</div>}<form className="composer" onSubmit={submit}><input value={input} onChange={event => setInput(event.target.value)} aria-label="질문 입력" placeholder="새로운 질문을 입력하세요"/><button type="submit" disabled={!input.trim() || loading} aria-label="질문 보내기"><PaperPlaneTilt size={16}/></button></form></section></div>; }

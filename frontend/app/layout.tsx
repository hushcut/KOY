import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Provenance — Luxury Heritage Atelier",
  description: "제품에 담긴 디자인 헤리티지를 발견하세요.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="ko" className="h-full antialiased"><body className="min-h-full flex flex-col">{children}</body></html>;
}

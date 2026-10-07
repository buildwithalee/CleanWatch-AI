import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CleanStreets AI | Agentic Waste Monitoring System",
  description:
    "CleanStreets AI is an agentic AI-powered waste monitoring system using computer vision and AI agents to detect and investigate possible waste dumping incidents for cleaner and smarter cities.",
  keywords: [
    "CleanStreets AI",
    "Agentic AI",
    "Waste Monitoring",
    "Computer Vision",
    "YOLO",
    "Google Gemini",
    "Smart Cities",
    "Waste Detection",
  ],
  authors: [
    {
      name: "Ali Raza Memon",
    },
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
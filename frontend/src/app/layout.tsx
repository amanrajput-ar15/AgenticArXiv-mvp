import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import "../styles/design-tokens.css";

export const metadata: Metadata = {
  title: "AgenticArXiv",
  description: "Multi-agent autonomous research system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body  suppressHydrationWarning={true}>
        <Navbar />
        <main style={{ paddingTop: "52px" }}>{children}</main>
      </body>
    </html>
  );
}

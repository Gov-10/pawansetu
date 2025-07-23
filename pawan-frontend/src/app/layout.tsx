//layout.tsx
export const metadata = {
  title: 'Home Page',
  description: 'Welcome page of my app',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
import React from 'react'
import Link from 'next/link';
const landingPage = () => {
  return (
    <div>
      <Link href="http://127.0.0.1:8000/sign_up/">Sign up</Link>
      <Link href="http://127.0.0.1:8000/login/">Login</Link>
    </div>
  )
}

export default landingPage;
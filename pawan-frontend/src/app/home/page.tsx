"use client";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface User {
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      // No token → redirect to Django login
      window.location.href = "http://127.0.0.1:8000/login/";
      return;
    }

    // Store token for future use
    localStorage.setItem("authToken", token);

    // Fetch user data
    fetchUserData(token);
  }, [searchParams]);

  const fetchUserData = async (token: string) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/user/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch user data");
      }

      const data: User = await res.json();
      setUser(data);
    } catch (err) {
      console.error(err);
      alert("Your session has expired. Please log in again.");
      window.location.href = "http://127.0.0.1:8000/login/";
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p className="p-4">Loading...</p>;

  return (
    <div className="p-4">
      {user ? (
        <div>
          <h1 className="text-2xl font-bold">Welcome, {user.username}!</h1>
          <p>Email: {user.email}</p>
        </div>
      ) : (
        <p>User not found. Please log in again.</p>
      )}
    </div>
  );
}

"use client"

import { useState } from "react"

export default function Home() {

  const [email,setEmail] = useState("")
  const [password,setPassword] = useState("")
  const [usage,setUsage] = useState<any>(null)

  async function login(){

    const res = await fetch(
      process.env.NEXT_PUBLIC_API_URL + "/auth/login",
      {
        method:"POST",
        headers:{ "Content-Type":"application/json"},
        body:JSON.stringify({email,password})
      }
    )

    const data = await res.json()

    localStorage.setItem("token",data.token)

    loadUsage(data.token)
  }

  async function loadUsage(token:string){

    const res = await fetch(
      process.env.NEXT_PUBLIC_API_URL + "/me/usage",
      {
        headers:{
          Authorization:"Bearer "+token
        }
      }
    )

    const data = await res.json()

    setUsage(data)
  }

  return (

    <div style={{
      height:"100vh",
      display:"flex",
      justifyContent:"center",
      alignItems:"center",
      flexDirection:"column",
      background:"#0f172a",
      color:"white",
      fontFamily:"sans-serif"
    }}>

      <h1>Client Portal</h1>

      {!usage && (
        <>
          <input
            placeholder="Email"
            value={email}
            onChange={e=>setEmail(e.target.value)}
            style={{margin:10,padding:10,width:250}}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e=>setPassword(e.target.value)}
            style={{margin:10,padding:10,width:250}}
          />

          <button
            onClick={login}
            style={{
              padding:10,
              width:250,
              background:"#2563eb",
              border:"none",
              color:"white",
              cursor:"pointer"
            }}
          >
            Login
          </button>
        </>
      )}

      {usage && (
        <div style={{marginTop:30}}>

          <h2>Usage</h2>

          <p>Upload: {usage.upload}</p>
          <p>Download: {usage.download}</p>
          <p>Total Used: {usage.used}</p>
          <p>Quota: {usage.quota}</p>

        </div>
      )}

    </div>
  )
}

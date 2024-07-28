"use client"

import { createTheme, CssBaseline, ThemeProvider } from "@mui/material"
import React from "react"

const theme = createTheme({
	palette: {
		mode: "dark",
	},
})

export default function App({ children }: Readonly<{ children: React.ReactNode }>) {
	return (
		<ThemeProvider theme={theme}>
			<CssBaseline />
			{children}
		</ThemeProvider>
	)
}

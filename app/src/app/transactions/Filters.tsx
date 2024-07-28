"use client"
import { Prisma } from "@prisma/client"

import { Checkbox, FormControlLabel, FormGroup, TextField } from "@mui/material"
import Stack from "@mui/material/Stack"
import React from "react"

interface FilterProps {
	years: number[]
	accounts: Prisma.$AccountsPayload["scalars"][]
	currencies: string[]
	filter: FilterState
	setFilter: (filter: FilterState) => void
}

export interface FilterState {
	search: string
	years: number[]
	months: number[]
	accounts: number[]
	type: ("incoming" | "outgoing")[]
	currencies: string[]
}

export const MONTHS = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
]

export default function Filters(props: FilterProps) {
	const [ctrlKey, setCtrlKey] = React.useState(false)

	React.useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent) => {
			if (e.key === "Control" || e.key === "Meta") setCtrlKey(true)
		}
		const handleKeyUp = (e: KeyboardEvent) => {
			if (e.key === "Control" || e.key === "Meta") setCtrlKey(false)
		}

		window.addEventListener("keydown", handleKeyDown)
		window.addEventListener("keyup", handleKeyUp)

		return () => {
			window.removeEventListener("keydown", handleKeyDown)
			window.removeEventListener("keyup", handleKeyUp)
		}
	}, [])

	function toggle(array: any[], item: any, all: any[]) {
		if (ctrlKey) {
			if (array.length === all.length) return []
			return all
		} else {
			if (array.includes(item)) return array.filter(i => i !== item)
			return [...array, item]
		}
	}

	return (
		<Stack direction="row">
			<FormGroup row>
				{props.accounts.map(account => (
					<FormControlLabel
						key={account.id}
						control={
							<Checkbox
								checked={props.filter.accounts.includes(account.id)}
								onChange={() =>
									props.setFilter({
										...props.filter,
										accounts: toggle(
											props.filter.accounts,
											account.id,
											props.accounts.map(a => a.id)
										),
									})
								}
							/>
						}
						label={account.name}
					/>
				))}
			</FormGroup>
			<FormGroup row>
				{["incoming", "outgoing"].map(type => (
					<FormControlLabel
						key={type}
						control={
							<Checkbox
								checked={props.filter.type.includes(type as "incoming" | "outgoing")}
								onChange={() =>
									props.setFilter({
										...props.filter,
										type: toggle(props.filter.type, type as "incoming" | "outgoing", ["incoming", "outgoing"]),
									})
								}
							/>
						}
						label={type}
					/>
				))}
			</FormGroup>

			<FormGroup row>
				{props.years.sort().map(year => (
					<FormControlLabel
						key={year}
						control={
							<Checkbox
								checked={props.filter.years.includes(year)}
								onChange={() =>
									props.setFilter({ ...props.filter, years: toggle(props.filter.years, year, props.years) })
								}
							/>
						}
						label={year}
					/>
				))}
			</FormGroup>
			<FormGroup row>
				{MONTHS.map((month, index) => (
					<FormControlLabel
						key={index}
						control={
							<Checkbox
								checked={props.filter.months.includes(index + 1)}
								onChange={() =>
									props.setFilter({
										...props.filter,
										months: toggle(
											props.filter.months,
											index + 1,
											MONTHS.map((_, i) => i + 1)
										),
									})
								}
							/>
						}
						label={month}
					/>
				))}
			</FormGroup>

			<FormGroup>
				<TextField
					size="small"
					variant="outlined"
					onChange={e => props.setFilter({ ...props.filter, search: e.target.value })}
					value={props.filter.search}
				/>
			</FormGroup>

			<FormGroup row>
				{props.currencies.map(currency => (
					<FormControlLabel
						key={currency}
						control={
							<Checkbox
								checked={props.filter.currencies.includes(currency)}
								onChange={() =>
									props.setFilter({
										...props.filter,
										currencies: toggle(props.filter.currencies, currency, props.currencies),
									})
								}
							/>
						}
						label={currency}
					/>
				))}
			</FormGroup>
		</Stack>
	)
}

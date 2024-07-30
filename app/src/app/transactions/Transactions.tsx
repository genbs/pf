"use client"
import { Prisma } from "@prisma/client"
import React, { useState } from "react"

import { useSearch } from "@/utils"
import { Stack } from "@mui/material"
import { DataGrid, GridColDef } from "@mui/x-data-grid"
import { Account, Tag, Transaction, TransactionTag } from "../types"
import Filters, { FilterState } from "./Filters"
import Occurrences from "./Occurences"

interface TransactionsProps {
	transactions: Transaction[]
	accounts: Account[]
	tags: Tag[]
}

const defaultFilterState: (years: number[], accounts: number[], currencies: string[]) => FilterState = (
	years,
	accounts,
	currencies
) => ({
	search: "",
	years,
	months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
	type: ["incoming", "outgoing"],
	accounts,
	currencies,
})

export default function Transactions(props: TransactionsProps) {
	const years = [...new Set(props.transactions.map(transaction => transaction.started_date.getFullYear()))]
	const currencies = [...new Set(props.transactions.map(transaction => transaction.currency))] as string[]

	const [selected, setSelected] = useState<number[]>([])

	const defaultFilter = defaultFilterState(
		years,
		props.accounts.map(account => account.id),
		currencies
	)

	let initialState = defaultFilter
	try {
		let storedState = JSON.parse(localStorage.getItem("filterState") || "{}")
		initialState = { ...defaultFilter, ...storedState }
	} catch (error) {}

	const [filterState, setFilterState] = useState<FilterState>(initialState)

	React.useEffect(() => {
		JSON.stringify(filterState) !== localStorage.getItem("filterState") &&
			localStorage.setItem("filterState", JSON.stringify(filterState))
	}, [filterState])

	const accountsMap = props.accounts.reduce((acc, account) => {
		acc[account.id] = account
		return acc
	}, {} as Record<number, Prisma.$AccountsPayload["scalars"]>)

	const columns: GridColDef[] = [
		{ field: "id", headerName: "ID", flex: 0 },
		{
			field: "started_date",
			headerName: "Started Date",
			flex: 1,
			valueGetter: params => (params as Date).toISOString(),
		},
		{ field: "type", headerName: "Type", flex: 0 },
		{ field: "description", headerName: "Description", flex: 4 },
		{ field: "label", headerName: "Label", flex: 4 },
		{ field: "amount", headerName: "Amount", flex: 1 },
		{ field: "currency", headerName: "Currency", flex: 1 },
		{
			field: "account_id",
			headerName: "Account",
			flex: 1,
			valueGetter: params => accountsMap[params as number]?.name ?? "Unknown",
		},
		{
			field: "fee",
			headerName: "Fee",
			flex: 1,
		},
		{
			field: "tags",
			headerName: "Tags",
			flex: 1,
			valueGetter: params =>
				(params as TransactionTag[]).map(tag => props.tags.find(t => tag.tag_id === t.id)?.name).join(", "),
		},
	]
	console.log(props.transactions)
	const fuseResults = useSearch(filterState.search, props.transactions, ["description", "label"])

	const transactions = props.transactions.filter(
		transaction =>
			filterState.years.includes(transaction.started_date.getFullYear()) &&
			filterState.months.includes(transaction.started_date.getMonth() + 1) &&
			filterState.accounts.includes(transaction.account_id) &&
			filterState.type.includes(transaction.type) &&
			(filterState.search === "" || fuseResults.some((result: any) => result.item.id === transaction.id))
	)

	function toMoney(amount: number) {
		return amount.toLocaleString("it-IT", {
			style: "currency",
			currency: "EUR",
		})
	}

	return (
		<div>
			<Filters
				years={years}
				accounts={props.accounts}
				currencies={currencies}
				filter={filterState}
				setFilter={setFilterState}
			/>

			<DataGrid
				onRowSelectionModelChange={newRowSelectionModel => {
					setSelected(newRowSelectionModel as number[])
				}}
				rowSelectionModel={selected}
				style={{ height: "60vh" }}
				rows={transactions}
				columns={columns}
				checkboxSelection
				pageSizeOptions={[10, 50, 100]}
			/>

			<div className="text-sm text-gray-500 mt-2">
				<Stack direction="row" gap="1rem">
					<span>INCOMING</span>
					<span>
						{toMoney(
							transactions
								.filter(t => t.type === "incoming")
								.reduce((acc, transaction) => acc + (transaction.amount + transaction.fee), 0)
						)}
					</span>
				</Stack>
				<Stack direction="row" gap="1rem">
					<span>OUTGOING</span>
					<span>
						{toMoney(
							transactions
								.filter(t => t.type === "outgoing")
								.reduce((acc, transaction) => acc + (transaction.amount + transaction.fee), 0)
						)}
					</span>
				</Stack>
				<Stack direction="row" gap="1rem">
					<span>TOTAL</span>
					<span>
						{toMoney(
							transactions
								.filter(t => t.type === "incoming")
								.reduce((acc, transaction) => acc + (transaction.amount + transaction.fee), 0) -
								transactions
									.filter(t => t.type === "outgoing")
									.reduce((acc, transaction) => acc + (transaction.amount + transaction.fee), 0)
						)}
					</span>
				</Stack>
			</div>

			<div>
				<Occurrences transactions={transactions} />
			</div>
		</div>
	)
}

import { Box, Button, Modal } from "@mui/material"
import React from "react"
import { Transaction } from "../types"

const style = {
	position: "absolute" as "absolute",
	top: "50%",
	left: "50%",
	transform: "translate(-50%, -50%)",
	width: 400,
	bgcolor: "background.paper",
	//border: "2px solid #000",
	boxShadow: 24,
	p: 4,
}

export default function TransactionModal({ transaction }: { transaction: Transaction }) {
	const [open, setOpen] = React.useState(false)

	const handleOpen = () => setOpen(true)
	const handleClose = () => setOpen(false)

	return (
		<>
			<Modal open={open} onClose={handleClose}>
				<Box sx={style}>
					<div>{transaction.id}</div>
					<div>{transaction.description}</div>
					<div>
						{transaction.amount} {transaction.currency}
					</div>
					<div>{transaction.completed_date.toISOString()}</div>
				</Box>
			</Modal>
			<Button onClick={handleOpen}>{transaction.id}</Button>
		</>
	)
}

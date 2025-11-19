return {
  {
    "mfussenegger/nvim-lint",
    opts = {
      linters = {
        ruff = {
          args = {
            "--config",
            vim.fn.expand("~/.config/nvim/ruff.toml"),
          },
        },
      },
    },
  },
}

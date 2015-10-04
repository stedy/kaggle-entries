#Naive Bayes approach focusing only on <p> and <h2> tags

library(tm)
library(XML)

#training <- read.csv("train_v2.csv")
training <- read.csv("train_head.csv")
spons.files <- paste0("all_data/", subset(training, sponsored == 1)$file)
native.files <- paste0("all_data/", subset(training, sponsored == 0)$file)

get.tdm <- function(doc.vec){
    control <- list(stopwords = TRUE, removePunctuation = TRUE,
                    removeNumbers = TRUE, minDocFreq = 2)
    doc.corpus <- Corpus(VectorSource(doc.vec))
    doc.dtm <- TermDocumentMatrix(doc.corpus, control)
    return(doc.dtm)
}

get.msg <- function(path){
    infile <- readLines(path, warn=F)
    if(length(infile > 0)){
    doc.html <- htmlTreeParse(path, useInternalNodes = T, xinclude=F)
    doc.html.name.value <- xpathApply(doc.html, '//h2|//p', xmlValue)
    doc.pasted <- paste(doc.html.name.value, collapse = ' ')
    return(doc.pasted)
    }
}

classify.email <- function(path, training.df, prior = 0.5, c = 1e-6){
    msg <- get.msg(path)
    msg.tdm <- get.tdm(msg)
    msg.freq <- rowSums(as.matrix(msg.tdm))
    msg.match <- intersect(names(msg.freq), training.df$term)

    if(length(msg.match) < 1)
          {
                return(prior * c ^ (length(msg.freq)))
      }
    else
          {
        match.probs <- training.df$occurrence[match(msg.match, training.df$term)]
        return(prior * prod(match.probs) * c ^ (length(msg.freq) - length(msg.match)))
          }
}

all.spons <- sapply(spons.files, get.msg)

# Create a DocumentTermMatrix from that vector
spons.tdm <- get.tdm(all.spons)

#feature set from the sponsored
spons.matrix <- as.matrix(spons.tdm)
spons.counts <- rowSums(spons.matrix)
spons.df <- data.frame(cbind(names(spons.counts),
                            as.numeric(spons.counts)),
                      stringsAsFactors = FALSE)
names(spons.df) <- c("term", "frequency")
spons.df$frequency <- as.numeric(spons.df$frequency)
spons.occurrence <- sapply(1:nrow(spons.matrix),
                          function(i)
                          {
                            length(which(spons.matrix[i, ] > 0)) / ncol(spons.matrix)
                          })
spons.density <- spons.df$frequency / sum(spons.df$frequency)
spons.df <- transform(spons.df,
                     density = spons.density,
                     occurrence = spons.occurrence)

#then the native
all.native <- sapply(native.files, get.msg)

# Create a DocumentTermMatrix from that vector
native.tdm <- get.tdm(all.native)

#feature set from the nativeored
native.matrix <- as.matrix(native.tdm)
native.counts <- rowSums(native.matrix)
native.df <- data.frame(cbind(names(native.counts),
                             as.numeric(native.counts)),
                       stringsAsFactors = FALSE)
names(native.df) <- c("term", "frequency")
native.df$frequency <- as.numeric(native.df$frequency)
native.occurrence <- sapply(1:nrow(native.matrix),
                           function(i)
                           {
                             length(which(native.matrix[i, ] > 0)) / ncol(native.matrix)
                           })
native.density <- native.df$frequency / sum(native.df$frequency)
native.df <- transform(native.df,
                      density = native.density,
                      occurrence = native.occurrence)

classifier <- function(path)
{
  pr.spons <- classify.email(path, spons.df)
  pr.native <- classify.email(path, native.df)
  return(c(pr.spons, pr.native, ifelse(pr.spons > pr.native, 1, 0)))
}

#testing files
empty <- "all_data/1004576_raw_html.txt"
goodtest <- "all_data/1000160_raw_html.txt"

test.files <- read.csv("sampleSubmission_v2.csv")
all.data <- list.files("all_data/5/")
pp <- intersect(test.files$file, all.data)

test1 <- classifier("119_raw_html.txt")
testbatch <- c("167_raw_html.txt", "329_raw_html.txt", "599_raw_html.txt")

batch.classifier <- lapply(testbatch, classifier(testbatch))
